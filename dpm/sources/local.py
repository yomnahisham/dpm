"""
local.py - for reading packages from local json/yaml files
"""

import json
import os
from typing import Optional, List
from pathlib import Path
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency


class LocalSource(Source):
    """for reading packages from local json/yaml files"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self._packages: dict = {}
        self._load_packages()
    
    def _load_packages(self):
        """load packages from json files in base_dir"""
        if not self.base_dir.exists():
            return
        
        for json_file in self.base_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # could be a single package or a list
                        if "name" in data:
                            name = data["name"]
                            self._packages[name] = data
                        elif isinstance(data, list):
                            for pkg in data:
                                if isinstance(pkg, dict) and "name" in pkg:
                                    name = pkg["name"]
                                    self._packages[name] = pkg
            except Exception:
                pass
    
    def get_language(self) -> str:
        return "local"
    
    def get_name(self) -> str:
        return "Local"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in local files"""
        return name in self._packages
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        if name not in self._packages:
            return []
        
        pkg_data = self._packages[name]
        if "version" in pkg_data:
            return [pkg_data["version"]]
        elif "versions" in pkg_data:
            if isinstance(pkg_data["versions"], list):
                return pkg_data["versions"]
            elif isinstance(pkg_data["versions"], dict):
                return list(pkg_data["versions"].keys())
        return []
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a local package"""
        if name not in self._packages:
            return None
        
        pkg_data = self._packages[name]
        pkg_version = version or pkg_data.get("version", "1.0.0")
        
        # determine language
        language = pkg_data.get("language", "local")
        
        package = Package(name, pkg_version, language)
        package.source = "local"
        
        # extract dependencies
        deps = []
        if "dependencies" in pkg_data:
            deps_data = pkg_data["dependencies"]
            if isinstance(deps_data, dict):
                for dep_name, dep_constraint in deps_data.items():
                    try:
                        if isinstance(dep_constraint, str):
                            dep_str = f"{dep_name}{dep_constraint}"
                        else:
                            dep_str = dep_name
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            elif isinstance(deps_data, list):
                for dep_str in deps_data:
                    try:
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
        
        package.dependencies = deps
        return package
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages in local files"""
        results = []
        query_lower = query.lower()
        
        for name, pkg_data in self._packages.items():
            if query_lower in name.lower():
                version = pkg_data.get("version", "1.0.0")
                description = pkg_data.get("description", "")
                results.append({
                    "name": name,
                    "version": version,
                    "description": description,
                    "source": "Local"
                })
                if len(results) >= limit:
                    break
        
        return results


"""

import json
import os
from typing import Optional, List
from pathlib import Path
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency


class LocalSource(Source):
    """for reading packages from local json/yaml files"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self._packages: dict = {}
        self._load_packages()
    
    def _load_packages(self):
        """load packages from json files in base_dir"""
        if not self.base_dir.exists():
            return
        
        for json_file in self.base_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # could be a single package or a list
                        if "name" in data:
                            name = data["name"]
                            self._packages[name] = data
                        elif isinstance(data, list):
                            for pkg in data:
                                if isinstance(pkg, dict) and "name" in pkg:
                                    name = pkg["name"]
                                    self._packages[name] = pkg
            except Exception:
                pass
    
    def get_language(self) -> str:
        return "local"
    
    def get_name(self) -> str:
        return "Local"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in local files"""
        return name in self._packages
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        if name not in self._packages:
            return []
        
        pkg_data = self._packages[name]
        if "version" in pkg_data:
            return [pkg_data["version"]]
        elif "versions" in pkg_data:
            if isinstance(pkg_data["versions"], list):
                return pkg_data["versions"]
            elif isinstance(pkg_data["versions"], dict):
                return list(pkg_data["versions"].keys())
        return []
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a local package"""
        if name not in self._packages:
            return None
        
        pkg_data = self._packages[name]
        pkg_version = version or pkg_data.get("version", "1.0.0")
        
        # determine language
        language = pkg_data.get("language", "local")
        
        package = Package(name, pkg_version, language)
        package.source = "local"
        
        # extract dependencies
        deps = []
        if "dependencies" in pkg_data:
            deps_data = pkg_data["dependencies"]
            if isinstance(deps_data, dict):
                for dep_name, dep_constraint in deps_data.items():
                    try:
                        if isinstance(dep_constraint, str):
                            dep_str = f"{dep_name}{dep_constraint}"
                        else:
                            dep_str = dep_name
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            elif isinstance(deps_data, list):
                for dep_str in deps_data:
                    try:
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
        
        package.dependencies = deps
        return package
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages in local files"""
        results = []
        query_lower = query.lower()
        
        for name, pkg_data in self._packages.items():
            if query_lower in name.lower():
                version = pkg_data.get("version", "1.0.0")
                description = pkg_data.get("description", "")
                results.append({
                    "name": name,
                    "version": version,
                    "description": description,
                    "source": "Local"
                })
                if len(results) >= limit:
                    break
        
        return results


"""

import json
import os
from typing import Optional, List
from pathlib import Path
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency


class LocalSource(Source):
    """for reading packages from local json/yaml files"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self._packages: dict = {}
        self._load_packages()
    
    def _load_packages(self):
        """load packages from json files in base_dir"""
        if not self.base_dir.exists():
            return
        
        for json_file in self.base_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # could be a single package or a list
                        if "name" in data:
                            name = data["name"]
                            self._packages[name] = data
                        elif isinstance(data, list):
                            for pkg in data:
                                if isinstance(pkg, dict) and "name" in pkg:
                                    name = pkg["name"]
                                    self._packages[name] = pkg
            except Exception:
                pass
    
    def get_language(self) -> str:
        return "local"
    
    def get_name(self) -> str:
        return "Local"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in local files"""
        return name in self._packages
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        if name not in self._packages:
            return []
        
        pkg_data = self._packages[name]
        if "version" in pkg_data:
            return [pkg_data["version"]]
        elif "versions" in pkg_data:
            if isinstance(pkg_data["versions"], list):
                return pkg_data["versions"]
            elif isinstance(pkg_data["versions"], dict):
                return list(pkg_data["versions"].keys())
        return []
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a local package"""
        if name not in self._packages:
            return None
        
        pkg_data = self._packages[name]
        pkg_version = version or pkg_data.get("version", "1.0.0")
        
        # determine language
        language = pkg_data.get("language", "local")
        
        package = Package(name, pkg_version, language)
        package.source = "local"
        
        # extract dependencies
        deps = []
        if "dependencies" in pkg_data:
            deps_data = pkg_data["dependencies"]
            if isinstance(deps_data, dict):
                for dep_name, dep_constraint in deps_data.items():
                    try:
                        if isinstance(dep_constraint, str):
                            dep_str = f"{dep_name}{dep_constraint}"
                        else:
                            dep_str = dep_name
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            elif isinstance(deps_data, list):
                for dep_str in deps_data:
                    try:
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
        
        package.dependencies = deps
        return package
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages in local files"""
        results = []
        query_lower = query.lower()
        
        for name, pkg_data in self._packages.items():
            if query_lower in name.lower():
                version = pkg_data.get("version", "1.0.0")
                description = pkg_data.get("description", "")
                results.append({
                    "name": name,
                    "version": version,
                    "description": description,
                    "source": "Local"
                })
                if len(results) >= limit:
                    break
        
        return results


"""

import json
import os
from typing import Optional, List
from pathlib import Path
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency


class LocalSource(Source):
    """for reading packages from local json/yaml files"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self._packages: dict = {}
        self._load_packages()
    
    def _load_packages(self):
        """load packages from json files in base_dir"""
        if not self.base_dir.exists():
            return
        
        for json_file in self.base_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # could be a single package or a list
                        if "name" in data:
                            name = data["name"]
                            self._packages[name] = data
                        elif isinstance(data, list):
                            for pkg in data:
                                if isinstance(pkg, dict) and "name" in pkg:
                                    name = pkg["name"]
                                    self._packages[name] = pkg
            except Exception:
                pass
    
    def get_language(self) -> str:
        return "local"
    
    def get_name(self) -> str:
        return "Local"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in local files"""
        return name in self._packages
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        if name not in self._packages:
            return []
        
        pkg_data = self._packages[name]
        if "version" in pkg_data:
            return [pkg_data["version"]]
        elif "versions" in pkg_data:
            if isinstance(pkg_data["versions"], list):
                return pkg_data["versions"]
            elif isinstance(pkg_data["versions"], dict):
                return list(pkg_data["versions"].keys())
        return []
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a local package"""
        if name not in self._packages:
            return None
        
        pkg_data = self._packages[name]
        pkg_version = version or pkg_data.get("version", "1.0.0")
        
        # determine language
        language = pkg_data.get("language", "local")
        
        package = Package(name, pkg_version, language)
        package.source = "local"
        
        # extract dependencies
        deps = []
        if "dependencies" in pkg_data:
            deps_data = pkg_data["dependencies"]
            if isinstance(deps_data, dict):
                for dep_name, dep_constraint in deps_data.items():
                    try:
                        if isinstance(dep_constraint, str):
                            dep_str = f"{dep_name}{dep_constraint}"
                        else:
                            dep_str = dep_name
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            elif isinstance(deps_data, list):
                for dep_str in deps_data:
                    try:
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
        
        package.dependencies = deps
        return package
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages in local files"""
        results = []
        query_lower = query.lower()
        
        for name, pkg_data in self._packages.items():
            if query_lower in name.lower():
                version = pkg_data.get("version", "1.0.0")
                description = pkg_data.get("description", "")
                results.append({
                    "name": name,
                    "version": version,
                    "description": description,
                    "source": "Local"
                })
                if len(results) >= limit:
                    break
        
        return results

