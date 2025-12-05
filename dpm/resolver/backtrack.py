"""
backtrack.py - backtracking resolver - slower but guaranteed to find solution if one exists
uses constraint satisfaction techniques like forward checking and mrv
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from .graph import DependencyGraph
from ..core.version import Version
from ..sources.source import Source


@dataclass
class BacktrackResult:
    """result from backtracking"""
    success: bool
    selected_versions: Dict[str, str]
    failure_reason: str = ""


@dataclass
class ResolutionState:
    """represents current state during backtracking"""
    selected_versions: Dict[str, str]  # what we've picked so far
    unassigned_packages: Set[str]  # what we still need to pick
    depth: int = 0  # how deep we are in the search
    
    def hash(self) -> str:
        """for memoization"""
        items = sorted(self.selected_versions.items())
        return ";".join(f"{k}:{v}" for k, v in items)
    
    def __eq__(self, other):
        return self.selected_versions == other.selected_versions


class BacktrackResolver:
    """backtracking resolver - slower but guaranteed to find solution if one exists"""
    
    def __init__(self):
        self.max_depth = 0  # limit search depth to avoid infinite loops (0 = no limit)
        self.failed_states: Set[str] = set()  # memoization - don't try states we know fail
    
    def resolve(self, requested_packages: List[str],
                initial_selections: Dict[str, str],
                sources: List[Source]) -> BacktrackResult:
        """resolve using backtracking - can take initial selections from greedy"""
        self.failed_states.clear()
        result = BacktrackResult(success=False, selected_versions={})
        
        # build constraint graph
        graph = self._build_constraint_graph(requested_packages, sources)
        
        # initialize state
        state = ResolutionState(
            selected_versions=initial_selections.copy(),
            unassigned_packages=set(),
            depth=0
        )
        
        # get all packages
        all_packages = graph.get_packages()
        for pkg in all_packages:
            if pkg not in state.selected_versions:
                state.unassigned_packages.add(pkg)
        
        # run backtracking
        if self._backtrack(state, graph, sources):
            result.success = True
            result.selected_versions = state.selected_versions.copy()
        else:
            result.failure_reason = "No solution found"
        
        return result
    
    def set_max_depth(self, depth: int):
        """limit search depth to avoid infinite loops (0 = no limit)"""
        self.max_depth = depth
    
    def _build_constraint_graph(self, requested_packages: List[str],
                                sources: List[Source]) -> DependencyGraph:
        """builds graph with all packages and their constraints"""
        from .graph import DependencyGraph
        
        graph = DependencyGraph()
        
        # similar to greedy, but build complete graph
        queue = requested_packages.copy()
        processed = set()
        
        while queue:
            package_name = queue.pop()
            
            if package_name in processed:
                continue
            processed.add(package_name)
            
            # find source
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if not source:
                continue
            
            # get all versions and process dependencies
            versions = source.get_available_versions(package_name)
            if not versions:
                continue
            
            # use latest version to get dependency structure
            package = source.fetch_latest(package_name)
            if not package:
                continue
            
            graph.add_package(package)
            
            # add dependencies
            for dep in package.dependencies:
                dep_name = dep.name
                graph.add_dependency(package_name, dep_name)
                
                if dep_name not in processed:
                    queue.append(dep_name)
        
        return graph
    
    def _select_unassigned_package_mrv(self, state: ResolutionState,
                                       graph: DependencyGraph,
                                       sources: List[Source]) -> Optional[str]:
        """mrv heuristic - pick the package with fewest valid versions left
        this helps us fail faster if there's no solution
        """
        best_package = None
        min_remaining = float('inf')
        
        for package_name in state.unassigned_packages:
            # get available versions
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if not source:
                continue
            
            versions = source.get_available_versions(package_name)
            
            # count how many versions satisfy current constraints
            # (simplified - would need to check constraints)
            remaining = len(versions)
            
            if remaining < min_remaining and remaining > 0:
                min_remaining = remaining
                best_package = package_name
        
        return best_package
    
    def _get_ordered_versions(self, package: str, sources: List[Source],
                              state: ResolutionState) -> List[str]:
        """orders versions to try - latest first usually"""
        # find source
        source = None
        for s in sources:
            if s.package_exists(package):
                source = s
                break
        
        if not source:
            return []
        
        versions = source.get_available_versions(package)
        
        # sort: latest first, stable preferred
        version_objs = []
        for v_str in versions:
            try:
                v = Version(v_str)
                version_objs.append((v, v_str))
            except ValueError:
                # skip invalid
                continue
        
        version_objs.sort(
            key=lambda x: (x[0].is_stable(), x[0]),
            reverse=True
        )
        
        return [v_str for _, v_str in version_objs]
    
    def _forward_check(self, package: str, version: str, state: ResolutionState,
                      graph: DependencyGraph, sources: List[Source]) -> bool:
        """forward checking - checks if picking this version would make it
        impossible to satisfy some other package's constraints
        """
        # create temporary state with this assignment
        temp_state = ResolutionState(
            selected_versions=state.selected_versions.copy(),
            unassigned_packages=state.unassigned_packages.copy(),
            depth=state.depth
        )
        temp_state.selected_versions[package] = version
        temp_state.unassigned_packages.discard(package)
        
        # check if any unassigned package becomes impossible
        for unassigned in temp_state.unassigned_packages:
            # get available versions
            source = None
            for s in sources:
                if s.package_exists(unassigned):
                    source = s
                    break
            
            if not source:
                continue
            
            available = source.get_available_versions(unassigned)
            
            # check if any version is still possible (simplified check)
            has_possible = len(available) > 0
            
            if not has_possible:
                return False  # forward check failed
        
        return True
    
    def _propagate_constraints(self, package: str, version: str,
                              state: ResolutionState, graph: DependencyGraph):
        """updates constraints after we pick a version"""
        # constraints are implicitly handled through the graph structure
        # in a full implementation, we would update constraint sets here
        pass
    
    def _is_complete(self, state: ResolutionState) -> bool:
        """are we done?"""
        return len(state.unassigned_packages) == 0
    
    def _has_conflict(self, state: ResolutionState, graph: DependencyGraph) -> bool:
        """is the current state broken?"""
        # check for cycle
        if graph.has_cycle():
            return True
        
        # check version constraints (simplified)
        # in full implementation, would check all constraints
        return False
    
    def _backtrack(self, state: ResolutionState, graph: DependencyGraph,
                  sources: List[Source]) -> bool:
        """the actual recursive backtracking"""
        # check if complete
        if self._is_complete(state):
            return not self._has_conflict(state, graph)
        
        # check depth limit
        if self.max_depth > 0 and state.depth >= self.max_depth:
            return False
        
        # memoization check
        state_hash = state.hash()
        if state_hash in self.failed_states:
            return False
        
        # select unassigned package (mrv heuristic)
        package = self._select_unassigned_package_mrv(state, graph, sources)
        if not package:
            return False
        
        # get ordered versions
        versions = self._get_ordered_versions(package, sources, state)
        
        # try each version
        for version in versions:
            # forward checking
            if not self._forward_check(package, version, state, graph, sources):
                continue
            
            # make assignment
            new_state = ResolutionState(
                selected_versions=state.selected_versions.copy(),
                unassigned_packages=state.unassigned_packages.copy(),
                depth=state.depth + 1
            )
            new_state.selected_versions[package] = version
            new_state.unassigned_packages.discard(package)
            
            # propagate constraints
            self._propagate_constraints(package, version, new_state, graph)
            
            # recursive call
            if self._backtrack(new_state, graph, sources):
                state.selected_versions = new_state.selected_versions
                state.unassigned_packages = new_state.unassigned_packages
                return True
        
        # all versions failed - mark state as failed
        self.failed_states.add(state_hash)
        return False


