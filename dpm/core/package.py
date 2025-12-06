"""
package.py - represents a package with name, version, and dependencies
"""

from typing import List
from .dependency import Dependency
from .version import Version


class Package:
    """represents a package with name, version, and its dependencies"""
    
    def __init__(self, name: str = "", version: str = "", language: str = ""):
        self.name = name
        self.version = version
        self.language = language  # python, javascript, system, etc
        self.source = ""  # where we got it from (pypi, npm, etc)
        self.dependencies: List[Dependency] = []
        self.integrity: Optional[str] = None  # sha256 checksum
    
    def get_version_obj(self) -> Version:
        """returns version as a Version object for comparison"""
        return Version(self.version)
    
    def add_dependency(self, dep: Dependency):
        """add a dependency"""
        self.dependencies.append(dep)
    
    def __str__(self) -> str:
        deps_str = ", ".join(str(d) for d in self.dependencies)
        return f"{self.name}@{self.version} ({self.language}) - deps: [{deps_str}]"
    
    def __repr__(self) -> str:
        return f"Package(name='{self.name}', version='{self.version}', language='{self.language}')"


"""

from typing import List
from .dependency import Dependency
from .version import Version


class Package:
    """represents a package with name, version, and its dependencies"""
    
    def __init__(self, name: str = "", version: str = "", language: str = ""):
        self.name = name
        self.version = version
        self.language = language  # python, javascript, system, etc
        self.source = ""  # where we got it from (pypi, npm, etc)
        self.dependencies: List[Dependency] = []
        self.integrity: Optional[str] = None  # sha256 checksum
    
    def get_version_obj(self) -> Version:
        """returns version as a Version object for comparison"""
        return Version(self.version)
    
    def add_dependency(self, dep: Dependency):
        """add a dependency"""
        self.dependencies.append(dep)
    
    def __str__(self) -> str:
        deps_str = ", ".join(str(d) for d in self.dependencies)
        return f"{self.name}@{self.version} ({self.language}) - deps: [{deps_str}]"
    
    def __repr__(self) -> str:
        return f"Package(name='{self.name}', version='{self.version}', language='{self.language}')"


"""

from typing import List
from .dependency import Dependency
from .version import Version


class Package:
    """represents a package with name, version, and its dependencies"""
    
    def __init__(self, name: str = "", version: str = "", language: str = ""):
        self.name = name
        self.version = version
        self.language = language  # python, javascript, system, etc
        self.source = ""  # where we got it from (pypi, npm, etc)
        self.dependencies: List[Dependency] = []
        self.integrity: Optional[str] = None  # sha256 checksum
    
    def get_version_obj(self) -> Version:
        """returns version as a Version object for comparison"""
        return Version(self.version)
    
    def add_dependency(self, dep: Dependency):
        """add a dependency"""
        self.dependencies.append(dep)
    
    def __str__(self) -> str:
        deps_str = ", ".join(str(d) for d in self.dependencies)
        return f"{self.name}@{self.version} ({self.language}) - deps: [{deps_str}]"
    
    def __repr__(self) -> str:
        return f"Package(name='{self.name}', version='{self.version}', language='{self.language}')"


"""

from typing import List
from .dependency import Dependency
from .version import Version


class Package:
    """represents a package with name, version, and its dependencies"""
    
    def __init__(self, name: str = "", version: str = "", language: str = ""):
        self.name = name
        self.version = version
        self.language = language  # python, javascript, system, etc
        self.source = ""  # where we got it from (pypi, npm, etc)
        self.dependencies: List[Dependency] = []
        self.integrity: Optional[str] = None  # sha256 checksum
    
    def get_version_obj(self) -> Version:
        """returns version as a Version object for comparison"""
        return Version(self.version)
    
    def add_dependency(self, dep: Dependency):
        """add a dependency"""
        self.dependencies.append(dep)
    
    def __str__(self) -> str:
        deps_str = ", ".join(str(d) for d in self.dependencies)
        return f"{self.name}@{self.version} ({self.language}) - deps: [{deps_str}]"
    
    def __repr__(self) -> str:
        return f"Package(name='{self.name}', version='{self.version}', language='{self.language}')"

