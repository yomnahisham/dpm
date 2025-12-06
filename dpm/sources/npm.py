"""
npm.py - for getting javascript packages from npm registry
"""

import json
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..network.http_client import HttpClient
from ..network.cache import Cache


class NpmSource(Source):
    """for getting javascript packages from npm registry"""
    
    API_BASE_URL = "https://registry.npmjs.org/"
    SEARCH_URL = "https://registry.npmjs.org/-/v1/search"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "javascript"
    
    def get_name(self) -> str:
        return "npm"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from npm"""
        cache_key = f"npm:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # fetch from npm
        url = f"{self.API_BASE_URL}{name}"
        response = self.http_client.get(url)
        
        if response:
            # cache the response
            if self.cache:
                self.cache.set(cache_key, response)
            return response
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages on npm"""
        url = f"{self.SEARCH_URL}?text={query}&size={limit}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "objects" in data:
                for item in data["objects"]:
                    pkg = item.get("package", {})
                    results.append({
                        "name": pkg.get("name", ""),
                        "version": pkg.get("version", ""),
                        "description": pkg.get("description", "")
                    })
        except (json.JSONDecodeError, KeyError):
            pass
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "versions" in data and isinstance(data["versions"], dict):
                for version in data["versions"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in npm"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        try:
            data = json.loads(metadata)
            return "name" in data and "versions" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse npm json response"""
        try:
            data = json.loads(json_str)
            
            if "versions" not in data or version not in data["versions"]:
                return None
            
            package = Package(name, version, "javascript")
            package.source = "npm"
            
            # extract dependencies
            version_data = data["versions"][version]
            deps = []
            
            if "dependencies" in version_data and isinstance(version_data["dependencies"], dict):
                for dep_name, dep_constraint in version_data["dependencies"].items():
                    try:
                        # npm uses semver ranges like "^1.0.0" or "~2.3.4"
                        dep_str = f"{dep_name}{dep_constraint}"
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            
            package.dependencies = deps
            return package
        except (json.JSONDecodeError, KeyError):
            return None
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, url in zip(names, urls):
            response = results.get(url)
            if response:
                cache_key = f"npm:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)

"""

import json
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..network.http_client import HttpClient
from ..network.cache import Cache


class NpmSource(Source):
    """for getting javascript packages from npm registry"""
    
    API_BASE_URL = "https://registry.npmjs.org/"
    SEARCH_URL = "https://registry.npmjs.org/-/v1/search"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "javascript"
    
    def get_name(self) -> str:
        return "npm"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from npm"""
        cache_key = f"npm:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # fetch from npm
        url = f"{self.API_BASE_URL}{name}"
        response = self.http_client.get(url)
        
        if response:
            # cache the response
            if self.cache:
                self.cache.set(cache_key, response)
            return response
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages on npm"""
        url = f"{self.SEARCH_URL}?text={query}&size={limit}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "objects" in data:
                for item in data["objects"]:
                    pkg = item.get("package", {})
                    results.append({
                        "name": pkg.get("name", ""),
                        "version": pkg.get("version", ""),
                        "description": pkg.get("description", "")
                    })
        except (json.JSONDecodeError, KeyError):
            pass
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "versions" in data and isinstance(data["versions"], dict):
                for version in data["versions"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in npm"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        try:
            data = json.loads(metadata)
            return "name" in data and "versions" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse npm json response"""
        try:
            data = json.loads(json_str)
            
            if "versions" not in data or version not in data["versions"]:
                return None
            
            package = Package(name, version, "javascript")
            package.source = "npm"
            
            # extract dependencies
            version_data = data["versions"][version]
            deps = []
            
            if "dependencies" in version_data and isinstance(version_data["dependencies"], dict):
                for dep_name, dep_constraint in version_data["dependencies"].items():
                    try:
                        # npm uses semver ranges like "^1.0.0" or "~2.3.4"
                        dep_str = f"{dep_name}{dep_constraint}"
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            
            package.dependencies = deps
            return package
        except (json.JSONDecodeError, KeyError):
            return None
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, url in zip(names, urls):
            response = results.get(url)
            if response:
                cache_key = f"npm:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)

"""

import json
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..network.http_client import HttpClient
from ..network.cache import Cache


class NpmSource(Source):
    """for getting javascript packages from npm registry"""
    
    API_BASE_URL = "https://registry.npmjs.org/"
    SEARCH_URL = "https://registry.npmjs.org/-/v1/search"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "javascript"
    
    def get_name(self) -> str:
        return "npm"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from npm"""
        cache_key = f"npm:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # fetch from npm
        url = f"{self.API_BASE_URL}{name}"
        response = self.http_client.get(url)
        
        if response:
            # cache the response
            if self.cache:
                self.cache.set(cache_key, response)
            return response
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages on npm"""
        url = f"{self.SEARCH_URL}?text={query}&size={limit}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "objects" in data:
                for item in data["objects"]:
                    pkg = item.get("package", {})
                    results.append({
                        "name": pkg.get("name", ""),
                        "version": pkg.get("version", ""),
                        "description": pkg.get("description", "")
                    })
        except (json.JSONDecodeError, KeyError):
            pass
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "versions" in data and isinstance(data["versions"], dict):
                for version in data["versions"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in npm"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        try:
            data = json.loads(metadata)
            return "name" in data and "versions" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse npm json response"""
        try:
            data = json.loads(json_str)
            
            if "versions" not in data or version not in data["versions"]:
                return None
            
            package = Package(name, version, "javascript")
            package.source = "npm"
            
            # extract dependencies
            version_data = data["versions"][version]
            deps = []
            
            if "dependencies" in version_data and isinstance(version_data["dependencies"], dict):
                for dep_name, dep_constraint in version_data["dependencies"].items():
                    try:
                        # npm uses semver ranges like "^1.0.0" or "~2.3.4"
                        dep_str = f"{dep_name}{dep_constraint}"
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            
            package.dependencies = deps
            return package
        except (json.JSONDecodeError, KeyError):
            return None
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, url in zip(names, urls):
            response = results.get(url)
            if response:
                cache_key = f"npm:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)

"""

import json
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..network.http_client import HttpClient
from ..network.cache import Cache


class NpmSource(Source):
    """for getting javascript packages from npm registry"""
    
    API_BASE_URL = "https://registry.npmjs.org/"
    SEARCH_URL = "https://registry.npmjs.org/-/v1/search"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "javascript"
    
    def get_name(self) -> str:
        return "npm"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from npm"""
        cache_key = f"npm:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # fetch from npm
        url = f"{self.API_BASE_URL}{name}"
        response = self.http_client.get(url)
        
        if response:
            # cache the response
            if self.cache:
                self.cache.set(cache_key, response)
            return response
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages on npm"""
        url = f"{self.SEARCH_URL}?text={query}&size={limit}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "objects" in data:
                for item in data["objects"]:
                    pkg = item.get("package", {})
                    results.append({
                        "name": pkg.get("name", ""),
                        "version": pkg.get("version", ""),
                        "description": pkg.get("description", "")
                    })
        except (json.JSONDecodeError, KeyError):
            pass
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "versions" in data and isinstance(data["versions"], dict):
                for version in data["versions"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in npm"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        try:
            data = json.loads(metadata)
            return "name" in data and "versions" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse npm json response"""
        try:
            data = json.loads(json_str)
            
            if "versions" not in data or version not in data["versions"]:
                return None
            
            package = Package(name, version, "javascript")
            package.source = "npm"
            
            # extract dependencies
            version_data = data["versions"][version]
            deps = []
            
            if "dependencies" in version_data and isinstance(version_data["dependencies"], dict):
                for dep_name, dep_constraint in version_data["dependencies"].items():
                    try:
                        # npm uses semver ranges like "^1.0.0" or "~2.3.4"
                        dep_str = f"{dep_name}{dep_constraint}"
                        dep = Dependency.parse(dep_str)
                        deps.append(dep)
                    except Exception:
                        pass
            
            package.dependencies = deps
            return package
        except (json.JSONDecodeError, KeyError):
            return None
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, url in zip(names, urls):
            response = results.get(url)
            if response:
                cache_key = f"npm:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)
