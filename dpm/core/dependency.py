"""
dependency.py - represents package dependencies and their constraints
"""

from typing import List, Optional
from .version import Version, VersionConstraint


class Dependency:
    """a dependency is just a package name with version constraints
    like "numpy>=1.0.0" or "flask~=2.0"
    """
    
    def __init__(self, name: str = "", constraints: Optional[List[VersionConstraint]] = None):
        self.name = name
        self.constraints = constraints or []
    
    @staticmethod
    def parse(dep_str: str) -> 'Dependency':
        """parses "numpy>=1.0.0,<2.0.0" into name and constraints"""
        # find where constraints start (first operator)
        operators = [">=", "<=", "!=", "==", "~", "^", ">", "<"]
        
        constraint_start = len(dep_str)
        for op in operators:
            idx = dep_str.find(op)
            if idx != -1 and idx < constraint_start:
                constraint_start = idx
        
        if constraint_start == len(dep_str):
            # no constraints, just package name
            return Dependency(dep_str.strip())
        
        name = dep_str[:constraint_start].strip()
        constraint_str = dep_str[constraint_start:].strip()
        
        constraints = VersionConstraint.parse_multiple(constraint_str)
        return Dependency(name, constraints)
    
    def satisfies(self, version: Version) -> bool:
        """checks if a version works for this dependency"""
        if not self.constraints:
            return True  # no constraints means any version works
        
        # all constraints must be satisfied
        for constraint in self.constraints:
            if not constraint.satisfies(version):
                return False
        return True
    
    def __str__(self) -> str:
        if not self.constraints:
            return self.name
        constraint_str = ",".join(str(c) for c in self.constraints)
        return f"{self.name}{constraint_str}"
    
    def __repr__(self) -> str:
        return f"Dependency('{self}')"


dependency.py - represents package dependencies and their constraints
"""

from typing import List, Optional
from .version import Version, VersionConstraint


class Dependency:
    """a dependency is just a package name with version constraints
    like "numpy>=1.0.0" or "flask~=2.0"
    """
    
    def __init__(self, name: str = "", constraints: Optional[List[VersionConstraint]] = None):
        self.name = name
        self.constraints = constraints or []
    
    @staticmethod
    def parse(dep_str: str) -> 'Dependency':
        """parses "numpy>=1.0.0,<2.0.0" into name and constraints"""
        # find where constraints start (first operator)
        operators = [">=", "<=", "!=", "==", "~", "^", ">", "<"]
        
        constraint_start = len(dep_str)
        for op in operators:
            idx = dep_str.find(op)
            if idx != -1 and idx < constraint_start:
                constraint_start = idx
        
        if constraint_start == len(dep_str):
            # no constraints, just package name
            return Dependency(dep_str.strip())
        
        name = dep_str[:constraint_start].strip()
        constraint_str = dep_str[constraint_start:].strip()
        
        constraints = VersionConstraint.parse_multiple(constraint_str)
        return Dependency(name, constraints)
    
    def satisfies(self, version: Version) -> bool:
        """checks if a version works for this dependency"""
        if not self.constraints:
            return True  # no constraints means any version works
        
        # all constraints must be satisfied
        for constraint in self.constraints:
            if not constraint.satisfies(version):
                return False
        return True
    
    def __str__(self) -> str:
        if not self.constraints:
            return self.name
        constraint_str = ",".join(str(c) for c in self.constraints)
        return f"{self.name}{constraint_str}"
    
    def __repr__(self) -> str:
        return f"Dependency('{self}')"


dependency.py - represents package dependencies and their constraints
"""

from typing import List, Optional
from .version import Version, VersionConstraint


class Dependency:
    """a dependency is just a package name with version constraints
    like "numpy>=1.0.0" or "flask~=2.0"
    """
    
    def __init__(self, name: str = "", constraints: Optional[List[VersionConstraint]] = None):
        self.name = name
        self.constraints = constraints or []
    
    @staticmethod
    def parse(dep_str: str) -> 'Dependency':
        """parses "numpy>=1.0.0,<2.0.0" into name and constraints"""
        # find where constraints start (first operator)
        operators = [">=", "<=", "!=", "==", "~", "^", ">", "<"]
        
        constraint_start = len(dep_str)
        for op in operators:
            idx = dep_str.find(op)
            if idx != -1 and idx < constraint_start:
                constraint_start = idx
        
        if constraint_start == len(dep_str):
            # no constraints, just package name
            return Dependency(dep_str.strip())
        
        name = dep_str[:constraint_start].strip()
        constraint_str = dep_str[constraint_start:].strip()
        
        constraints = VersionConstraint.parse_multiple(constraint_str)
        return Dependency(name, constraints)
    
    def satisfies(self, version: Version) -> bool:
        """checks if a version works for this dependency"""
        if not self.constraints:
            return True  # no constraints means any version works
        
        # all constraints must be satisfied
        for constraint in self.constraints:
            if not constraint.satisfies(version):
                return False
        return True
    
    def __str__(self) -> str:
        if not self.constraints:
            return self.name
        constraint_str = ",".join(str(c) for c in self.constraints)
        return f"{self.name}{constraint_str}"
    
    def __repr__(self) -> str:
        return f"Dependency('{self}')"


dependency.py - represents package dependencies and their constraints
"""

from typing import List, Optional
from .version import Version, VersionConstraint


class Dependency:
    """a dependency is just a package name with version constraints
    like "numpy>=1.0.0" or "flask~=2.0"
    """
    
    def __init__(self, name: str = "", constraints: Optional[List[VersionConstraint]] = None):
        self.name = name
        self.constraints = constraints or []
    
    @staticmethod
    def parse(dep_str: str) -> 'Dependency':
        """parses "numpy>=1.0.0,<2.0.0" into name and constraints"""
        # find where constraints start (first operator)
        operators = [">=", "<=", "!=", "==", "~", "^", ">", "<"]
        
        constraint_start = len(dep_str)
        for op in operators:
            idx = dep_str.find(op)
            if idx != -1 and idx < constraint_start:
                constraint_start = idx
        
        if constraint_start == len(dep_str):
            # no constraints, just package name
            return Dependency(dep_str.strip())
        
        name = dep_str[:constraint_start].strip()
        constraint_str = dep_str[constraint_start:].strip()
        
        constraints = VersionConstraint.parse_multiple(constraint_str)
        return Dependency(name, constraints)
    
    def satisfies(self, version: Version) -> bool:
        """checks if a version works for this dependency"""
        if not self.constraints:
            return True  # no constraints means any version works
        
        # all constraints must be satisfied
        for constraint in self.constraints:
            if not constraint.satisfies(version):
                return False
        return True
    
    def __str__(self) -> str:
        if not self.constraints:
            return self.name
        constraint_str = ",".join(str(c) for c in self.constraints)
        return f"{self.name}{constraint_str}"
    
    def __repr__(self) -> str:
        return f"Dependency('{self}')"




