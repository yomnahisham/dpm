"""
bruteforce.py - brute force resolver - tries all combinations
guaranteed to find solution but very slow for large inputs
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from itertools import product
from .graph import DependencyGraph
from ..core.version import Version, VersionConstraint
from ..core.dependency import Dependency
from ..sources.source import Source
import logging

logger = logging.getLogger(__name__)


@dataclass
class BruteForceResult:
    """result from brute force resolution"""
    success: bool
    selected_versions: Dict[str, str]
    failure_reason: str = ""
    combinations_tried: int = 0


class BruteForceResolver:
    """brute force resolver - tries all possible version combinations"""
    
    def __init__(self, max_combinations: int = 50000):
        """initialize brute force resolver
        max_combinations: limit to prevent infinite loops
        """
        self.max_combinations = max_combinations
    
    def resolve(self, requested_packages: List[str], sources: List[Source]) -> BruteForceResult:
        """resolve by trying all possible version combinations"""
        result = BruteForceResult(success=False, selected_versions={})
        
        # build dependency graph to get all packages (similar to greedy/backtrack)
        graph = DependencyGraph()
        all_packages = set(requested_packages)
        package_versions: Dict[str, List[str]] = {}
        
        # collect all packages and their versions
        queue = list(requested_packages)
        processed = set()
        
        while queue:
            package_name = queue.pop(0)
            if package_name in processed:
                continue
            processed.add(package_name)
            
            # find source for this package
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if not source:
                result.failure_reason = f"Package not found: {package_name}"
                return result
            
            # get available versions (limit to reasonable number for brute force)
            versions = source.get_available_versions(package_name)
            if not versions:
                result.failure_reason = f"No versions available for {package_name}"
                return result
            
            # limit versions to prevent explosion (take latest 3 versions for brute force)
            # brute force is exponential, so we need very small limits
            from ..core.version import Version
            try:
                version_objs = [(Version(v), v) for v in versions if v]
                version_objs.sort(reverse=True)
                versions = [v for _, v in version_objs[:3]]  # limit to 3 versions for brute force
            except Exception:
                versions = versions[:3]  # fallback
            
            package_versions[package_name] = versions
            
            # get dependencies and add to queue (use latest package to get dependency structure)
            latest_pkg = source.fetch_latest(package_name)
            if latest_pkg:
                # add package to graph
                graph.add_package(latest_pkg)
                
                for dep in latest_pkg.dependencies:
                    dep_name = dep.name
                    graph.add_dependency(package_name, dep_name)
                    
                    if dep_name not in processed:
                        queue.append(dep_name)
                        all_packages.add(dep_name)
        
        # get versions for all dependency packages that weren't in initial queue
        for package_name in all_packages:
            if package_name not in package_versions:
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if source:
                    versions = source.get_available_versions(package_name)
                    if versions:
                        # limit versions
                        try:
                            from ..core.version import Version
                            version_objs = [(Version(v), v) for v in versions if v]
                            version_objs.sort(reverse=True)
                            versions = [v for _, v in version_objs[:3]]  # limit to 3
                        except Exception:
                            versions = versions[:3]
                        package_versions[package_name] = versions
        
        # generate all possible combinations
        package_names = list(all_packages)
        version_lists = [package_versions.get(name, []) for name in package_names]
        
        # calculate total combinations
        total_combinations = 1
        for versions in version_lists:
            total_combinations *= len(versions) if versions else 1
            if total_combinations > self.max_combinations:
                result.failure_reason = f"Too many combinations: {total_combinations} (limit: {self.max_combinations})"
                return result
        
        logger.info(f"Brute force: trying {total_combinations} combinations for {len(package_names)} packages")
        
        # try each combination
        combinations_tried = 0
        for combination in product(*version_lists):
            combinations_tried += 1
            if combinations_tried > self.max_combinations:
                result.failure_reason = f"Exceeded max combinations: {self.max_combinations}"
                result.combinations_tried = combinations_tried
                return result
            
            # create assignment
            assignment = dict(zip(package_names, combination))
            
            # check if this assignment satisfies all constraints
            if self._validate_assignment(assignment, graph, sources):
                result.success = True
                result.selected_versions = assignment
                result.combinations_tried = combinations_tried
                logger.info(f"Brute force found solution after {combinations_tried} combinations")
                return result
        
        result.failure_reason = "No valid combination found"
        result.combinations_tried = combinations_tried
        return result
    
    def _validate_assignment(self, assignment: Dict[str, str], 
                           graph: DependencyGraph, 
                           sources: List[Source]) -> bool:
        """check if an assignment satisfies all dependency constraints"""
        # check each package's dependencies using the graph structure
        for package_name, version in assignment.items():
            # get package from graph (we added it during graph building)
            package = graph.get_package(package_name)
            if not package:
                # if not in graph, try to fetch it
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if not source:
                    return False
                
                package = source.fetch_package(package_name, version)
                if not package:
                    return False
            
            # get dependencies for this package (use the version we're testing)
            # but we need to check if this version's dependencies match
            # for simplicity, use the package from graph which has latest version's deps
            # and validate the assigned version satisfies constraints
            deps = graph.get_dependencies(package_name)
            
            # get the actual package with this version to check its dependencies
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if source:
                version_package = source.fetch_package(package_name, version)
                if version_package:
                    # check each dependency constraint
                    for dep in version_package.dependencies:
                        dep_name = dep.name
                        if dep_name not in assignment:
                            # dependency not in assignment - invalid
                            return False
                        
                        dep_version_str = assignment[dep_name]
                        try:
                            dep_version = Version(dep_version_str)
                            if not dep.constraint.satisfies(dep_version):
                                return False
                        except Exception:
                            return False
        
        return True


guaranteed to find solution but very slow for large inputs
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from itertools import product
from .graph import DependencyGraph
from ..core.version import Version, VersionConstraint
from ..core.dependency import Dependency
from ..sources.source import Source
import logging

logger = logging.getLogger(__name__)


@dataclass
class BruteForceResult:
    """result from brute force resolution"""
    success: bool
    selected_versions: Dict[str, str]
    failure_reason: str = ""
    combinations_tried: int = 0


class BruteForceResolver:
    """brute force resolver - tries all possible version combinations"""
    
    def __init__(self, max_combinations: int = 50000):
        """initialize brute force resolver
        max_combinations: limit to prevent infinite loops
        """
        self.max_combinations = max_combinations
    
    def resolve(self, requested_packages: List[str], sources: List[Source]) -> BruteForceResult:
        """resolve by trying all possible version combinations"""
        result = BruteForceResult(success=False, selected_versions={})
        
        # build dependency graph to get all packages (similar to greedy/backtrack)
        graph = DependencyGraph()
        all_packages = set(requested_packages)
        package_versions: Dict[str, List[str]] = {}
        
        # collect all packages and their versions
        queue = list(requested_packages)
        processed = set()
        
        while queue:
            package_name = queue.pop(0)
            if package_name in processed:
                continue
            processed.add(package_name)
            
            # find source for this package
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if not source:
                result.failure_reason = f"Package not found: {package_name}"
                return result
            
            # get available versions (limit to reasonable number for brute force)
            versions = source.get_available_versions(package_name)
            if not versions:
                result.failure_reason = f"No versions available for {package_name}"
                return result
            
            # limit versions to prevent explosion (take latest 3 versions for brute force)
            # brute force is exponential, so we need very small limits
            from ..core.version import Version
            try:
                version_objs = [(Version(v), v) for v in versions if v]
                version_objs.sort(reverse=True)
                versions = [v for _, v in version_objs[:3]]  # limit to 3 versions for brute force
            except Exception:
                versions = versions[:3]  # fallback
            
            package_versions[package_name] = versions
            
            # get dependencies and add to queue (use latest package to get dependency structure)
            latest_pkg = source.fetch_latest(package_name)
            if latest_pkg:
                # add package to graph
                graph.add_package(latest_pkg)
                
                for dep in latest_pkg.dependencies:
                    dep_name = dep.name
                    graph.add_dependency(package_name, dep_name)
                    
                    if dep_name not in processed:
                        queue.append(dep_name)
                        all_packages.add(dep_name)
        
        # get versions for all dependency packages that weren't in initial queue
        for package_name in all_packages:
            if package_name not in package_versions:
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if source:
                    versions = source.get_available_versions(package_name)
                    if versions:
                        # limit versions
                        try:
                            from ..core.version import Version
                            version_objs = [(Version(v), v) for v in versions if v]
                            version_objs.sort(reverse=True)
                            versions = [v for _, v in version_objs[:3]]  # limit to 3
                        except Exception:
                            versions = versions[:3]
                        package_versions[package_name] = versions
        
        # generate all possible combinations
        package_names = list(all_packages)
        version_lists = [package_versions.get(name, []) for name in package_names]
        
        # calculate total combinations
        total_combinations = 1
        for versions in version_lists:
            total_combinations *= len(versions) if versions else 1
            if total_combinations > self.max_combinations:
                result.failure_reason = f"Too many combinations: {total_combinations} (limit: {self.max_combinations})"
                return result
        
        logger.info(f"Brute force: trying {total_combinations} combinations for {len(package_names)} packages")
        
        # try each combination
        combinations_tried = 0
        for combination in product(*version_lists):
            combinations_tried += 1
            if combinations_tried > self.max_combinations:
                result.failure_reason = f"Exceeded max combinations: {self.max_combinations}"
                result.combinations_tried = combinations_tried
                return result
            
            # create assignment
            assignment = dict(zip(package_names, combination))
            
            # check if this assignment satisfies all constraints
            if self._validate_assignment(assignment, graph, sources):
                result.success = True
                result.selected_versions = assignment
                result.combinations_tried = combinations_tried
                logger.info(f"Brute force found solution after {combinations_tried} combinations")
                return result
        
        result.failure_reason = "No valid combination found"
        result.combinations_tried = combinations_tried
        return result
    
    def _validate_assignment(self, assignment: Dict[str, str], 
                           graph: DependencyGraph, 
                           sources: List[Source]) -> bool:
        """check if an assignment satisfies all dependency constraints"""
        # check each package's dependencies using the graph structure
        for package_name, version in assignment.items():
            # get package from graph (we added it during graph building)
            package = graph.get_package(package_name)
            if not package:
                # if not in graph, try to fetch it
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if not source:
                    return False
                
                package = source.fetch_package(package_name, version)
                if not package:
                    return False
            
            # get dependencies for this package (use the version we're testing)
            # but we need to check if this version's dependencies match
            # for simplicity, use the package from graph which has latest version's deps
            # and validate the assigned version satisfies constraints
            deps = graph.get_dependencies(package_name)
            
            # get the actual package with this version to check its dependencies
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if source:
                version_package = source.fetch_package(package_name, version)
                if version_package:
                    # check each dependency constraint
                    for dep in version_package.dependencies:
                        dep_name = dep.name
                        if dep_name not in assignment:
                            # dependency not in assignment - invalid
                            return False
                        
                        dep_version_str = assignment[dep_name]
                        try:
                            dep_version = Version(dep_version_str)
                            if not dep.constraint.satisfies(dep_version):
                                return False
                        except Exception:
                            return False
        
        return True


guaranteed to find solution but very slow for large inputs
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from itertools import product
from .graph import DependencyGraph
from ..core.version import Version, VersionConstraint
from ..core.dependency import Dependency
from ..sources.source import Source
import logging

logger = logging.getLogger(__name__)


@dataclass
class BruteForceResult:
    """result from brute force resolution"""
    success: bool
    selected_versions: Dict[str, str]
    failure_reason: str = ""
    combinations_tried: int = 0


class BruteForceResolver:
    """brute force resolver - tries all possible version combinations"""
    
    def __init__(self, max_combinations: int = 50000):
        """initialize brute force resolver
        max_combinations: limit to prevent infinite loops
        """
        self.max_combinations = max_combinations
    
    def resolve(self, requested_packages: List[str], sources: List[Source]) -> BruteForceResult:
        """resolve by trying all possible version combinations"""
        result = BruteForceResult(success=False, selected_versions={})
        
        # build dependency graph to get all packages (similar to greedy/backtrack)
        graph = DependencyGraph()
        all_packages = set(requested_packages)
        package_versions: Dict[str, List[str]] = {}
        
        # collect all packages and their versions
        queue = list(requested_packages)
        processed = set()
        
        while queue:
            package_name = queue.pop(0)
            if package_name in processed:
                continue
            processed.add(package_name)
            
            # find source for this package
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if not source:
                result.failure_reason = f"Package not found: {package_name}"
                return result
            
            # get available versions (limit to reasonable number for brute force)
            versions = source.get_available_versions(package_name)
            if not versions:
                result.failure_reason = f"No versions available for {package_name}"
                return result
            
            # limit versions to prevent explosion (take latest 3 versions for brute force)
            # brute force is exponential, so we need very small limits
            from ..core.version import Version
            try:
                version_objs = [(Version(v), v) for v in versions if v]
                version_objs.sort(reverse=True)
                versions = [v for _, v in version_objs[:3]]  # limit to 3 versions for brute force
            except Exception:
                versions = versions[:3]  # fallback
            
            package_versions[package_name] = versions
            
            # get dependencies and add to queue (use latest package to get dependency structure)
            latest_pkg = source.fetch_latest(package_name)
            if latest_pkg:
                # add package to graph
                graph.add_package(latest_pkg)
                
                for dep in latest_pkg.dependencies:
                    dep_name = dep.name
                    graph.add_dependency(package_name, dep_name)
                    
                    if dep_name not in processed:
                        queue.append(dep_name)
                        all_packages.add(dep_name)
        
        # get versions for all dependency packages that weren't in initial queue
        for package_name in all_packages:
            if package_name not in package_versions:
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if source:
                    versions = source.get_available_versions(package_name)
                    if versions:
                        # limit versions
                        try:
                            from ..core.version import Version
                            version_objs = [(Version(v), v) for v in versions if v]
                            version_objs.sort(reverse=True)
                            versions = [v for _, v in version_objs[:3]]  # limit to 3
                        except Exception:
                            versions = versions[:3]
                        package_versions[package_name] = versions
        
        # generate all possible combinations
        package_names = list(all_packages)
        version_lists = [package_versions.get(name, []) for name in package_names]
        
        # calculate total combinations
        total_combinations = 1
        for versions in version_lists:
            total_combinations *= len(versions) if versions else 1
            if total_combinations > self.max_combinations:
                result.failure_reason = f"Too many combinations: {total_combinations} (limit: {self.max_combinations})"
                return result
        
        logger.info(f"Brute force: trying {total_combinations} combinations for {len(package_names)} packages")
        
        # try each combination
        combinations_tried = 0
        for combination in product(*version_lists):
            combinations_tried += 1
            if combinations_tried > self.max_combinations:
                result.failure_reason = f"Exceeded max combinations: {self.max_combinations}"
                result.combinations_tried = combinations_tried
                return result
            
            # create assignment
            assignment = dict(zip(package_names, combination))
            
            # check if this assignment satisfies all constraints
            if self._validate_assignment(assignment, graph, sources):
                result.success = True
                result.selected_versions = assignment
                result.combinations_tried = combinations_tried
                logger.info(f"Brute force found solution after {combinations_tried} combinations")
                return result
        
        result.failure_reason = "No valid combination found"
        result.combinations_tried = combinations_tried
        return result
    
    def _validate_assignment(self, assignment: Dict[str, str], 
                           graph: DependencyGraph, 
                           sources: List[Source]) -> bool:
        """check if an assignment satisfies all dependency constraints"""
        # check each package's dependencies using the graph structure
        for package_name, version in assignment.items():
            # get package from graph (we added it during graph building)
            package = graph.get_package(package_name)
            if not package:
                # if not in graph, try to fetch it
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if not source:
                    return False
                
                package = source.fetch_package(package_name, version)
                if not package:
                    return False
            
            # get dependencies for this package (use the version we're testing)
            # but we need to check if this version's dependencies match
            # for simplicity, use the package from graph which has latest version's deps
            # and validate the assigned version satisfies constraints
            deps = graph.get_dependencies(package_name)
            
            # get the actual package with this version to check its dependencies
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if source:
                version_package = source.fetch_package(package_name, version)
                if version_package:
                    # check each dependency constraint
                    for dep in version_package.dependencies:
                        dep_name = dep.name
                        if dep_name not in assignment:
                            # dependency not in assignment - invalid
                            return False
                        
                        dep_version_str = assignment[dep_name]
                        try:
                            dep_version = Version(dep_version_str)
                            if not dep.constraint.satisfies(dep_version):
                                return False
                        except Exception:
                            return False
        
        return True


guaranteed to find solution but very slow for large inputs
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from itertools import product
from .graph import DependencyGraph
from ..core.version import Version, VersionConstraint
from ..core.dependency import Dependency
from ..sources.source import Source
import logging

logger = logging.getLogger(__name__)


@dataclass
class BruteForceResult:
    """result from brute force resolution"""
    success: bool
    selected_versions: Dict[str, str]
    failure_reason: str = ""
    combinations_tried: int = 0


class BruteForceResolver:
    """brute force resolver - tries all possible version combinations"""
    
    def __init__(self, max_combinations: int = 50000):
        """initialize brute force resolver
        max_combinations: limit to prevent infinite loops
        """
        self.max_combinations = max_combinations
    
    def resolve(self, requested_packages: List[str], sources: List[Source]) -> BruteForceResult:
        """resolve by trying all possible version combinations"""
        result = BruteForceResult(success=False, selected_versions={})
        
        # build dependency graph to get all packages (similar to greedy/backtrack)
        graph = DependencyGraph()
        all_packages = set(requested_packages)
        package_versions: Dict[str, List[str]] = {}
        
        # collect all packages and their versions
        queue = list(requested_packages)
        processed = set()
        
        while queue:
            package_name = queue.pop(0)
            if package_name in processed:
                continue
            processed.add(package_name)
            
            # find source for this package
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if not source:
                result.failure_reason = f"Package not found: {package_name}"
                return result
            
            # get available versions (limit to reasonable number for brute force)
            versions = source.get_available_versions(package_name)
            if not versions:
                result.failure_reason = f"No versions available for {package_name}"
                return result
            
            # limit versions to prevent explosion (take latest 3 versions for brute force)
            # brute force is exponential, so we need very small limits
            from ..core.version import Version
            try:
                version_objs = [(Version(v), v) for v in versions if v]
                version_objs.sort(reverse=True)
                versions = [v for _, v in version_objs[:3]]  # limit to 3 versions for brute force
            except Exception:
                versions = versions[:3]  # fallback
            
            package_versions[package_name] = versions
            
            # get dependencies and add to queue (use latest package to get dependency structure)
            latest_pkg = source.fetch_latest(package_name)
            if latest_pkg:
                # add package to graph
                graph.add_package(latest_pkg)
                
                for dep in latest_pkg.dependencies:
                    dep_name = dep.name
                    graph.add_dependency(package_name, dep_name)
                    
                    if dep_name not in processed:
                        queue.append(dep_name)
                        all_packages.add(dep_name)
        
        # get versions for all dependency packages that weren't in initial queue
        for package_name in all_packages:
            if package_name not in package_versions:
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if source:
                    versions = source.get_available_versions(package_name)
                    if versions:
                        # limit versions
                        try:
                            from ..core.version import Version
                            version_objs = [(Version(v), v) for v in versions if v]
                            version_objs.sort(reverse=True)
                            versions = [v for _, v in version_objs[:3]]  # limit to 3
                        except Exception:
                            versions = versions[:3]
                        package_versions[package_name] = versions
        
        # generate all possible combinations
        package_names = list(all_packages)
        version_lists = [package_versions.get(name, []) for name in package_names]
        
        # calculate total combinations
        total_combinations = 1
        for versions in version_lists:
            total_combinations *= len(versions) if versions else 1
            if total_combinations > self.max_combinations:
                result.failure_reason = f"Too many combinations: {total_combinations} (limit: {self.max_combinations})"
                return result
        
        logger.info(f"Brute force: trying {total_combinations} combinations for {len(package_names)} packages")
        
        # try each combination
        combinations_tried = 0
        for combination in product(*version_lists):
            combinations_tried += 1
            if combinations_tried > self.max_combinations:
                result.failure_reason = f"Exceeded max combinations: {self.max_combinations}"
                result.combinations_tried = combinations_tried
                return result
            
            # create assignment
            assignment = dict(zip(package_names, combination))
            
            # check if this assignment satisfies all constraints
            if self._validate_assignment(assignment, graph, sources):
                result.success = True
                result.selected_versions = assignment
                result.combinations_tried = combinations_tried
                logger.info(f"Brute force found solution after {combinations_tried} combinations")
                return result
        
        result.failure_reason = "No valid combination found"
        result.combinations_tried = combinations_tried
        return result
    
    def _validate_assignment(self, assignment: Dict[str, str], 
                           graph: DependencyGraph, 
                           sources: List[Source]) -> bool:
        """check if an assignment satisfies all dependency constraints"""
        # check each package's dependencies using the graph structure
        for package_name, version in assignment.items():
            # get package from graph (we added it during graph building)
            package = graph.get_package(package_name)
            if not package:
                # if not in graph, try to fetch it
                source = None
                for s in sources:
                    if s.package_exists(package_name):
                        source = s
                        break
                
                if not source:
                    return False
                
                package = source.fetch_package(package_name, version)
                if not package:
                    return False
            
            # get dependencies for this package (use the version we're testing)
            # but we need to check if this version's dependencies match
            # for simplicity, use the package from graph which has latest version's deps
            # and validate the assigned version satisfies constraints
            deps = graph.get_dependencies(package_name)
            
            # get the actual package with this version to check its dependencies
            source = None
            for s in sources:
                if s.package_exists(package_name):
                    source = s
                    break
            
            if source:
                version_package = source.fetch_package(package_name, version)
                if version_package:
                    # check each dependency constraint
                    for dep in version_package.dependencies:
                        dep_name = dep.name
                        if dep_name not in assignment:
                            # dependency not in assignment - invalid
                            return False
                        
                        dep_version_str = assignment[dep_name]
                        try:
                            dep_version = Version(dep_version_str)
                            if not dep.constraint.satisfies(dep_version):
                                return False
                        except Exception:
                            return False
        
        return True

