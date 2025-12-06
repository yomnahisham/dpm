"""
plan.py - installation plan for ordering packages by dependencies
"""

from typing import List, Dict
from ..resolver.graph import DependencyGraph
from ..core.package import Package


class InstallationPlan:
    """installation plan - orders packages by dependencies"""
    
    def __init__(self, packages: Dict[str, str], dependency_map: Dict[str, List[str]]):
        """
        packages: dict of package name -> version
        dependency_map: dict of package name -> list of dependency names
        """
        self.packages = packages
        self.dependency_map = dependency_map
        self.ordered_packages: List[str] = []
        self._build_plan()
    
    def _build_plan(self):
        """build installation plan using topological sort"""
        # build graph
        graph = DependencyGraph()
        
        # add all packages
        for name in self.packages.keys():
            # create dummy package for graph
            pkg = Package(name, self.packages[name], "unknown")
            graph.add_package(pkg)
        
        # add dependencies
        for name, deps in self.dependency_map.items():
            for dep in deps:
                if dep in self.packages:  # only add if dependency is in our package set
                    graph.add_dependency(name, dep)
        
        # get topological order
        self.ordered_packages = graph.topological_sort()
        
        # if topological sort failed (cycle), just use original order
        if not self.ordered_packages:
            self.ordered_packages = list(self.packages.keys())
    
    def get_ordered_packages(self) -> List[tuple]:
        """get ordered list of (name, version) tuples"""
        return [(name, self.packages[name]) for name in self.ordered_packages if name in self.packages]
    
    def can_install_parallel(self, package: str) -> bool:
        """check if package can be installed in parallel with others"""
        # simplified: packages with no dependencies can be installed in parallel
        deps = self.dependency_map.get(package, [])
        return len(deps) == 0
    
    def get_parallel_groups(self) -> List[List[str]]:
        """get groups of packages that can be installed in parallel"""
        groups = []
        remaining = set(self.ordered_packages)
        installed = set()
        
        while remaining:
            # find packages with all dependencies installed
            ready = []
            for pkg in remaining:
                deps = self.dependency_map.get(pkg, [])
                if all(dep in installed for dep in deps):
                    ready.append(pkg)
            
            if ready:
                groups.append(ready)
                for pkg in ready:
                    installed.add(pkg)
                    remaining.remove(pkg)
            else:
                # circular dependency or error - install remaining one by one
                groups.append([remaining.pop()])
        
        return groups


plan.py - installation plan for ordering packages by dependencies
"""

from typing import List, Dict
from ..resolver.graph import DependencyGraph
from ..core.package import Package


class InstallationPlan:
    """installation plan - orders packages by dependencies"""
    
    def __init__(self, packages: Dict[str, str], dependency_map: Dict[str, List[str]]):
        """
        packages: dict of package name -> version
        dependency_map: dict of package name -> list of dependency names
        """
        self.packages = packages
        self.dependency_map = dependency_map
        self.ordered_packages: List[str] = []
        self._build_plan()
    
    def _build_plan(self):
        """build installation plan using topological sort"""
        # build graph
        graph = DependencyGraph()
        
        # add all packages
        for name in self.packages.keys():
            # create dummy package for graph
            pkg = Package(name, self.packages[name], "unknown")
            graph.add_package(pkg)
        
        # add dependencies
        for name, deps in self.dependency_map.items():
            for dep in deps:
                if dep in self.packages:  # only add if dependency is in our package set
                    graph.add_dependency(name, dep)
        
        # get topological order
        self.ordered_packages = graph.topological_sort()
        
        # if topological sort failed (cycle), just use original order
        if not self.ordered_packages:
            self.ordered_packages = list(self.packages.keys())
    
    def get_ordered_packages(self) -> List[tuple]:
        """get ordered list of (name, version) tuples"""
        return [(name, self.packages[name]) for name in self.ordered_packages if name in self.packages]
    
    def can_install_parallel(self, package: str) -> bool:
        """check if package can be installed in parallel with others"""
        # simplified: packages with no dependencies can be installed in parallel
        deps = self.dependency_map.get(package, [])
        return len(deps) == 0
    
    def get_parallel_groups(self) -> List[List[str]]:
        """get groups of packages that can be installed in parallel"""
        groups = []
        remaining = set(self.ordered_packages)
        installed = set()
        
        while remaining:
            # find packages with all dependencies installed
            ready = []
            for pkg in remaining:
                deps = self.dependency_map.get(pkg, [])
                if all(dep in installed for dep in deps):
                    ready.append(pkg)
            
            if ready:
                groups.append(ready)
                for pkg in ready:
                    installed.add(pkg)
                    remaining.remove(pkg)
            else:
                # circular dependency or error - install remaining one by one
                groups.append([remaining.pop()])
        
        return groups


plan.py - installation plan for ordering packages by dependencies
"""

from typing import List, Dict
from ..resolver.graph import DependencyGraph
from ..core.package import Package


class InstallationPlan:
    """installation plan - orders packages by dependencies"""
    
    def __init__(self, packages: Dict[str, str], dependency_map: Dict[str, List[str]]):
        """
        packages: dict of package name -> version
        dependency_map: dict of package name -> list of dependency names
        """
        self.packages = packages
        self.dependency_map = dependency_map
        self.ordered_packages: List[str] = []
        self._build_plan()
    
    def _build_plan(self):
        """build installation plan using topological sort"""
        # build graph
        graph = DependencyGraph()
        
        # add all packages
        for name in self.packages.keys():
            # create dummy package for graph
            pkg = Package(name, self.packages[name], "unknown")
            graph.add_package(pkg)
        
        # add dependencies
        for name, deps in self.dependency_map.items():
            for dep in deps:
                if dep in self.packages:  # only add if dependency is in our package set
                    graph.add_dependency(name, dep)
        
        # get topological order
        self.ordered_packages = graph.topological_sort()
        
        # if topological sort failed (cycle), just use original order
        if not self.ordered_packages:
            self.ordered_packages = list(self.packages.keys())
    
    def get_ordered_packages(self) -> List[tuple]:
        """get ordered list of (name, version) tuples"""
        return [(name, self.packages[name]) for name in self.ordered_packages if name in self.packages]
    
    def can_install_parallel(self, package: str) -> bool:
        """check if package can be installed in parallel with others"""
        # simplified: packages with no dependencies can be installed in parallel
        deps = self.dependency_map.get(package, [])
        return len(deps) == 0
    
    def get_parallel_groups(self) -> List[List[str]]:
        """get groups of packages that can be installed in parallel"""
        groups = []
        remaining = set(self.ordered_packages)
        installed = set()
        
        while remaining:
            # find packages with all dependencies installed
            ready = []
            for pkg in remaining:
                deps = self.dependency_map.get(pkg, [])
                if all(dep in installed for dep in deps):
                    ready.append(pkg)
            
            if ready:
                groups.append(ready)
                for pkg in ready:
                    installed.add(pkg)
                    remaining.remove(pkg)
            else:
                # circular dependency or error - install remaining one by one
                groups.append([remaining.pop()])
        
        return groups


plan.py - installation plan for ordering packages by dependencies
"""

from typing import List, Dict
from ..resolver.graph import DependencyGraph
from ..core.package import Package


class InstallationPlan:
    """installation plan - orders packages by dependencies"""
    
    def __init__(self, packages: Dict[str, str], dependency_map: Dict[str, List[str]]):
        """
        packages: dict of package name -> version
        dependency_map: dict of package name -> list of dependency names
        """
        self.packages = packages
        self.dependency_map = dependency_map
        self.ordered_packages: List[str] = []
        self._build_plan()
    
    def _build_plan(self):
        """build installation plan using topological sort"""
        # build graph
        graph = DependencyGraph()
        
        # add all packages
        for name in self.packages.keys():
            # create dummy package for graph
            pkg = Package(name, self.packages[name], "unknown")
            graph.add_package(pkg)
        
        # add dependencies
        for name, deps in self.dependency_map.items():
            for dep in deps:
                if dep in self.packages:  # only add if dependency is in our package set
                    graph.add_dependency(name, dep)
        
        # get topological order
        self.ordered_packages = graph.topological_sort()
        
        # if topological sort failed (cycle), just use original order
        if not self.ordered_packages:
            self.ordered_packages = list(self.packages.keys())
    
    def get_ordered_packages(self) -> List[tuple]:
        """get ordered list of (name, version) tuples"""
        return [(name, self.packages[name]) for name in self.ordered_packages if name in self.packages]
    
    def can_install_parallel(self, package: str) -> bool:
        """check if package can be installed in parallel with others"""
        # simplified: packages with no dependencies can be installed in parallel
        deps = self.dependency_map.get(package, [])
        return len(deps) == 0
    
    def get_parallel_groups(self) -> List[List[str]]:
        """get groups of packages that can be installed in parallel"""
        groups = []
        remaining = set(self.ordered_packages)
        installed = set()
        
        while remaining:
            # find packages with all dependencies installed
            ready = []
            for pkg in remaining:
                deps = self.dependency_map.get(pkg, [])
                if all(dep in installed for dep in deps):
                    ready.append(pkg)
            
            if ready:
                groups.append(ready)
                for pkg in ready:
                    installed.add(pkg)
                    remaining.remove(pkg)
            else:
                # circular dependency or error - install remaining one by one
                groups.append([remaining.pop()])
        
        return groups


