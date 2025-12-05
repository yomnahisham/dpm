"""
graph.py - dependency graph for managing package relationships
"""

from typing import Dict, List, Set, Optional
from ..core.package import Package


class DependencyGraph:
    """dependency graph for managing package relationships"""
    
    def __init__(self):
        self.packages: Dict[str, Package] = {}  # package name -> package
        self.dependencies: Dict[str, List[str]] = {}  # package -> list of dependencies
        self.dependents: Dict[str, List[str]] = {}  # package -> list of packages that depend on it
    
    def add_package(self, package: Package):
        """add a package to the graph"""
        self.packages[package.name] = package
        if package.name not in self.dependencies:
            self.dependencies[package.name] = []
        if package.name not in self.dependents:
            self.dependents[package.name] = []
    
    def add_dependency(self, package: str, dependency: str):
        """add a dependency edge: package depends on dependency"""
        if package not in self.dependencies:
            self.dependencies[package] = []
        if dependency not in self.dependencies[package]:
            self.dependencies[package].append(dependency)
        
        # update dependents
        if dependency not in self.dependents:
            self.dependents[dependency] = []
        if package not in self.dependents[dependency]:
            self.dependents[dependency].append(package)
    
    def get_package(self, name: str) -> Optional[Package]:
        """get a package by name"""
        return self.packages.get(name)
    
    def get_dependencies(self, name: str) -> List[str]:
        """get dependencies of a package"""
        return self.dependencies.get(name, [])
    
    def get_dependents(self, name: str) -> List[str]:
        """get packages that depend on this one"""
        return self.dependents.get(name, [])
    
    def get_packages(self) -> List[str]:
        """get all package names"""
        return list(self.packages.keys())
    
    def has_cycle(self) -> bool:
        """check if the graph has a cycle"""
        return len(self._find_cycle()) > 0
    
    def get_cycle(self) -> List[str]:
        """get a cycle if one exists"""
        return self._find_cycle()
    
    def _find_cycle(self) -> List[str]:
        """find a cycle using dfs"""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycle_path: List[str] = []
        
        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # found a cycle
                    cycle_start = path.index(neighbor)
                    cycle_path.extend(path[cycle_start:] + [neighbor])
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for node in self.packages.keys():
            if node not in visited:
                if dfs(node, []):
                    return cycle_path
        
        return []
    
    def topological_sort(self) -> List[str]:
        """topological sort of packages (dependencies before dependents)"""
        # build reverse graph: what depends on what
        reverse_deps: Dict[str, List[str]] = {pkg: [] for pkg in self.packages.keys()}
        for pkg, deps in self.dependencies.items():
            for dep in deps:
                if dep in reverse_deps:
                    reverse_deps[dep].append(pkg)
        
        # calculate in-degrees (how many dependencies this package has)
        in_degree: Dict[str, int] = {}
        for pkg in self.packages.keys():
            in_degree[pkg] = len(self.dependencies.get(pkg, []))
        
        # kahn's algorithm - start with packages that have no dependencies
        queue = [pkg for pkg, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # for each package that depends on this node, decrease its in-degree
            for dependent in reverse_deps.get(node, []):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # if we didn't process all nodes, there's a cycle
        if len(result) != len(self.packages):
            return []
        
        return result

