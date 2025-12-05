"""
greedy.py - greedy resolver - fast but might not find solution if there are conflicts
basically just picks the latest version that works and hopes for the best
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .graph import DependencyGraph
from ..core.package import Package
from ..core.version import Version, VersionConstraint
from ..core.dependency import Dependency
from ..sources.source import Source


@dataclass
class GreedyResult:
    """result from greedy resolution attempt"""
    success: bool
    selected_versions: Dict[str, str]  # what versions we picked
    conflict_package: str = ""  # which package caused issues
    conflict_reason: str = ""
    not_found_packages: List[str] = None  # packages we couldn't find anywhere
    conflict_details: Dict[str, List[str]] = None  # package -> list of conflicting requirements
    
    def __post_init__(self):
        if self.not_found_packages is None:
            self.not_found_packages = []
        if self.conflict_details is None:
            self.conflict_details = {}


class GreedyResolver:
    """greedy resolver - fast but might not find solution if there are conflicts"""
    
    def __init__(self):
        self.selected_versions: Dict[str, str] = {}
    
    def resolve(self, requested_packages: List[str], sources: List[Source]) -> GreedyResult:
        """try to resolve using greedy approach"""
        self.selected_versions.clear()
        result = GreedyResult(success=False, selected_versions={})
        
        # build dependency graph
        graph, not_found = self._build_graph_with_errors(requested_packages, sources)
        result.not_found_packages = not_found
        
        # if any requested package was not found, fail immediately
        for pkg in requested_packages:
            if pkg in not_found:
                result.conflict_package = pkg
                result.conflict_reason = f"Package not found in any source: {pkg}"
                return result
        
        # check for cycles
        if graph.has_cycle():
            result.conflict_reason = "Circular dependency detected"
            cycle = graph.get_cycle()
            if cycle:
                result.conflict_package = cycle[0]
            return result
        
        # topological sort to get resolution order
        resolution_order = graph.topological_sort()
        if not resolution_order:
            result.conflict_reason = "Failed to determine resolution order"
            return result
        
        # resolve each package in order
        for package_name in resolution_order:
            # find source for this package
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if not source:
                result.conflict_package = package_name
                result.conflict_reason = f"Package not found in any source: {package_name}"
                return result
            
            # get available versions
            available_versions = source.get_available_versions(package_name)
            if not available_versions:
                result.conflict_package = package_name
                result.conflict_reason = f"No versions available for: {package_name}"
                return result
            
            # get constraints from dependents
            constraints = self._get_constraints(package_name, graph)
            
            # select best version using greedy heuristics
            best_version = self._select_best_version(
                package_name, available_versions, constraints, sources
            )
            
            if not best_version:
                result.conflict_package = package_name
                result.conflict_reason = f"No version satisfies constraints for: {package_name}"
                return result
            
            self.selected_versions[package_name] = best_version
        
        result.success = True
        result.selected_versions = self.selected_versions.copy()
        return result
    
    def _build_graph_with_errors(self, requested_packages: List[str], 
                                 sources: List[Source]) -> Tuple[DependencyGraph, List[str]]:
        """builds the dependency graph and tracks which packages we couldn't find"""
        graph = DependencyGraph()
        not_found = []
        
        # queue for bfs traversal
        queue = requested_packages.copy()
        processed = set()
        
        # prefetch initial packages in parallel
        for source in sources:
            source.prefetch(requested_packages)
        
        while queue:
            # batch process: collect unprocessed packages
            batch = []
            while queue and len(batch) < 10:
                pkg = queue.pop()
                if pkg not in processed:
                    batch.append(pkg)
                    processed.add(pkg)
            
            if not batch:
                continue
            
            # prefetch batch dependencies
            for source in sources:
                source.prefetch(batch)
            
            # process batch
            for package_name in batch:
                # find source for this package
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if not source:
                    not_found.append(package_name)
                    continue
                
                # get latest version (greedy: try latest first)
                package = source.fetch_latest(package_name)
                if not package:
                    not_found.append(package_name)
                    continue
                
                graph.add_package(package)
                
                # collect dependencies for next batch prefetch
                deps_to_prefetch = []
                for dep in package.dependencies:
                    dep_name = dep.name
                    graph.add_dependency(package_name, dep_name)
                    
                    if dep_name not in processed:
                        queue.append(dep_name)
                        deps_to_prefetch.append(dep_name)
                
                # prefetch dependencies
                if deps_to_prefetch:
                    for s in sources:
                        s.prefetch(deps_to_prefetch)
        
        return graph, not_found
    
    def _get_constraints(self, package: str, graph: DependencyGraph) -> List[VersionConstraint]:
        """gets all the constraints on a package from things that depend on it"""
        constraints = []
        
        # get all dependents (packages that depend on this one)
        dependents = graph.get_dependents(package)
        
        for dependent in dependents:
            dep_package = graph.get_package(dependent)
            if not dep_package:
                continue
            
            # find constraint for this package in dependent's dependencies
            for dep in dep_package.dependencies:
                if dep.name == package:
                    constraints.extend(dep.constraints)
        
        return constraints
    
    def _score_version(self, version: Version, constraints: List[VersionConstraint],
                      selected: Dict[str, str]) -> int:
        """scores a version - higher is better"""
        score = 0
        
        # prefer stable versions
        if version.is_stable():
            score += 1000
        
        # prefer newer versions (higher major/minor/patch)
        score += version.major * 100
        score += version.minor * 10
        score += version.patch
        
        # check if this version is already selected (reuse optimization)
        for selected_version_str in selected.values():
            try:
                selected_version = Version(selected_version_str)
                if selected_version == version:
                    score += 500  # bonus for reusing
            except ValueError:
                pass
        
        return score
    
    def _select_best_version(self, package: str, available_versions: List[str],
                           constraints: List[VersionConstraint],
                           sources: List[Source]) -> Optional[str]:
        """picks the best version based on our heuristics
        prefers: latest stable > latest prerelease > already selected
        """
        valid_versions = []  # (version_obj, version_str)
        
        # filter versions by constraints
        for version_str in available_versions:
            try:
                version = Version(version_str)
                
                # check if version satisfies all constraints
                satisfies_all = True
                for constraint in constraints:
                    if not constraint.satisfies(version):
                        satisfies_all = False
                        break
                
                if satisfies_all:
                    valid_versions.append((version, version_str))
            except ValueError:
                # skip invalid versions
                continue
        
        if not valid_versions:
            return None
        
        # sort by score (greedy heuristic)
        valid_versions.sort(
            key=lambda x: self._score_version(x[0], constraints, self.selected_versions),
            reverse=True
        )
        
        return valid_versions[0][1]

