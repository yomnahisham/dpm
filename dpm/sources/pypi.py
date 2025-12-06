"""
pypi.py - for getting python packages from pypi.org
"""

import json
import logging
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..core.validation import sanitize_package_name, ValidationError
from ..network.http_client import HttpClient
from ..network.cache import Cache
from ..installer.integrity import Integrity

logger = logging.getLogger(__name__)


class PyPISource(Source):
    """for getting python packages from pypi.org"""
    
    API_BASE_URL = "https://pypi.org/pypi/"
    SEARCH_URL = "https://pypi.org/search/"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        self._prefetch_cache: Dict[str, Optional[str]] = {}
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "python"
    
    def get_name(self) -> str:
        return "PyPI"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from pypi"""
        # sanitize package name
        try:
            name = sanitize_package_name(name)
        except ValidationError as e:
            logger.error(f"Invalid package name: {e}")
            return None
        
        cache_key = f"pypi:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {name}")
                return cached
        
        # fetch from pypi
        url = f"{self.API_BASE_URL}{name}/json"
        logger.debug(f"Fetching {url}")
        response = self.http_client.get(url)
        
        if response:
            # validate response is valid JSON
            try:
                json.loads(response)  # validate it's JSON
                # cache the response
                if self.cache:
                    self.cache.set(cache_key, response)
                logger.debug(f"Successfully fetched and cached {name}")
                return response
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for {name}: {e}")
                return None
        else:
            logger.warning(f"Failed to fetch metadata for {name} from {url}")
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """search for packages on pypi"""
        # PyPI search API endpoint
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        url = f"{self.API_BASE_URL}search/?q={encoded_query}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "results" in data:
                for item in data["results"][:limit]:
                    results.append({
                        "name": item.get("name", ""),
                        "version": item.get("version", ""),
                        "description": item.get("summary", "")
                    })
        except (json.JSONDecodeError, KeyError):
            # fallback: try simple package name check
            # if query looks like a package name, try fetching it
            if query.replace("_", "").replace("-", "").isalnum():
                if self.package_exists(query):
                    pkg = self.fetch_latest(query)
                    if pkg:
                        results.append({
                            "name": pkg.name,
                            "version": pkg.version,
                            "description": ""
                        })
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "releases" in data and isinstance(data["releases"], dict):
                # directly extract version keys from releases object
                for version in data["releases"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in pypi"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        # verify it's valid json with expected structure
        try:
            data = json.loads(metadata)
            return "info" in data and "releases" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse pypi json response"""
        try:
            data = json.loads(json_str)
            
            if "info" not in data:
                return None
            
            package = Package(name, version, "python")
            package.source = "PyPI"
            
            # extract dependencies
            deps = self._extract_dependencies(json_str, version)
            package.dependencies = deps
            
            # try to get checksum from releases
            if "releases" in data and version in data["releases"]:
                releases = data["releases"][version]
                if releases and len(releases) > 0:
                    # get first release (usually source distribution)
                    release = releases[0]
                    if "digests" in release and "sha256" in release["digests"]:
                        package.integrity = Integrity.format_integrity(release["digests"]["sha256"])
            
            return package
        except json.JSONDecodeError:
            return None
    
    def _extract_dependencies(self, json_str: str, version: str) -> List[Dependency]:
        """extract dependencies from pypi metadata"""
        deps = []
        
        try:
            data = json.loads(json_str)
            
            if ("info" in data and 
                "requires_dist" in data["info"] and 
                data["info"]["requires_dist"] is not None):
                
                for dep_str in data["info"]["requires_dist"]:
                    if isinstance(dep_str, str):
                        # skip optional dependencies (those with "extra" markers)
                        if "extra ==" in dep_str:
                            continue
                        
                        # parse dependency string (e.g., "numpy>=1.0.0")
                        # remove any markers after semicolon
                        if ';' in dep_str:
                            dep_str = dep_str.split(';')[0]
                        
                        dep_str = dep_str.strip()
                        
                        if dep_str:
                            try:
                                dep = Dependency.parse(dep_str)
                                deps.append(dep)
                            except Exception:
                                pass
        except (json.JSONDecodeError, KeyError):
            pass
        
        return deps
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}/json" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, response in zip(names, [results.get(url) for url in urls]):
            if response:
                cache_key = f"pypi:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)
                self._prefetch_cache[name] = response
            else:
                self._prefetch_cache[name] = None

"""

import json
import logging
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..core.validation import sanitize_package_name, ValidationError
from ..network.http_client import HttpClient
from ..network.cache import Cache
from ..installer.integrity import Integrity

logger = logging.getLogger(__name__)


class PyPISource(Source):
    """for getting python packages from pypi.org"""
    
    API_BASE_URL = "https://pypi.org/pypi/"
    SEARCH_URL = "https://pypi.org/search/"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        self._prefetch_cache: Dict[str, Optional[str]] = {}
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "python"
    
    def get_name(self) -> str:
        return "PyPI"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from pypi"""
        # sanitize package name
        try:
            name = sanitize_package_name(name)
        except ValidationError as e:
            logger.error(f"Invalid package name: {e}")
            return None
        
        cache_key = f"pypi:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {name}")
                return cached
        
        # fetch from pypi
        url = f"{self.API_BASE_URL}{name}/json"
        logger.debug(f"Fetching {url}")
        response = self.http_client.get(url)
        
        if response:
            # validate response is valid JSON
            try:
                json.loads(response)  # validate it's JSON
                # cache the response
                if self.cache:
                    self.cache.set(cache_key, response)
                logger.debug(f"Successfully fetched and cached {name}")
                return response
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for {name}: {e}")
                return None
        else:
            logger.warning(f"Failed to fetch metadata for {name} from {url}")
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """search for packages on pypi"""
        # PyPI search API endpoint
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        url = f"{self.API_BASE_URL}search/?q={encoded_query}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "results" in data:
                for item in data["results"][:limit]:
                    results.append({
                        "name": item.get("name", ""),
                        "version": item.get("version", ""),
                        "description": item.get("summary", "")
                    })
        except (json.JSONDecodeError, KeyError):
            # fallback: try simple package name check
            # if query looks like a package name, try fetching it
            if query.replace("_", "").replace("-", "").isalnum():
                if self.package_exists(query):
                    pkg = self.fetch_latest(query)
                    if pkg:
                        results.append({
                            "name": pkg.name,
                            "version": pkg.version,
                            "description": ""
                        })
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "releases" in data and isinstance(data["releases"], dict):
                # directly extract version keys from releases object
                for version in data["releases"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in pypi"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        # verify it's valid json with expected structure
        try:
            data = json.loads(metadata)
            return "info" in data and "releases" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse pypi json response"""
        try:
            data = json.loads(json_str)
            
            if "info" not in data:
                return None
            
            package = Package(name, version, "python")
            package.source = "PyPI"
            
            # extract dependencies
            deps = self._extract_dependencies(json_str, version)
            package.dependencies = deps
            
            # try to get checksum from releases
            if "releases" in data and version in data["releases"]:
                releases = data["releases"][version]
                if releases and len(releases) > 0:
                    # get first release (usually source distribution)
                    release = releases[0]
                    if "digests" in release and "sha256" in release["digests"]:
                        package.integrity = Integrity.format_integrity(release["digests"]["sha256"])
            
            return package
        except json.JSONDecodeError:
            return None
    
    def _extract_dependencies(self, json_str: str, version: str) -> List[Dependency]:
        """extract dependencies from pypi metadata"""
        deps = []
        
        try:
            data = json.loads(json_str)
            
            if ("info" in data and 
                "requires_dist" in data["info"] and 
                data["info"]["requires_dist"] is not None):
                
                for dep_str in data["info"]["requires_dist"]:
                    if isinstance(dep_str, str):
                        # skip optional dependencies (those with "extra" markers)
                        if "extra ==" in dep_str:
                            continue
                        
                        # parse dependency string (e.g., "numpy>=1.0.0")
                        # remove any markers after semicolon
                        if ';' in dep_str:
                            dep_str = dep_str.split(';')[0]
                        
                        dep_str = dep_str.strip()
                        
                        if dep_str:
                            try:
                                dep = Dependency.parse(dep_str)
                                deps.append(dep)
                            except Exception:
                                pass
        except (json.JSONDecodeError, KeyError):
            pass
        
        return deps
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}/json" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, response in zip(names, [results.get(url) for url in urls]):
            if response:
                cache_key = f"pypi:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)
                self._prefetch_cache[name] = response
            else:
                self._prefetch_cache[name] = None

"""

import json
import logging
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..core.validation import sanitize_package_name, ValidationError
from ..network.http_client import HttpClient
from ..network.cache import Cache
from ..installer.integrity import Integrity

logger = logging.getLogger(__name__)


class PyPISource(Source):
    """for getting python packages from pypi.org"""
    
    API_BASE_URL = "https://pypi.org/pypi/"
    SEARCH_URL = "https://pypi.org/search/"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        self._prefetch_cache: Dict[str, Optional[str]] = {}
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "python"
    
    def get_name(self) -> str:
        return "PyPI"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from pypi"""
        # sanitize package name
        try:
            name = sanitize_package_name(name)
        except ValidationError as e:
            logger.error(f"Invalid package name: {e}")
            return None
        
        cache_key = f"pypi:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {name}")
                return cached
        
        # fetch from pypi
        url = f"{self.API_BASE_URL}{name}/json"
        logger.debug(f"Fetching {url}")
        response = self.http_client.get(url)
        
        if response:
            # validate response is valid JSON
            try:
                json.loads(response)  # validate it's JSON
                # cache the response
                if self.cache:
                    self.cache.set(cache_key, response)
                logger.debug(f"Successfully fetched and cached {name}")
                return response
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for {name}: {e}")
                return None
        else:
            logger.warning(f"Failed to fetch metadata for {name} from {url}")
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """search for packages on pypi"""
        # PyPI search API endpoint
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        url = f"{self.API_BASE_URL}search/?q={encoded_query}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "results" in data:
                for item in data["results"][:limit]:
                    results.append({
                        "name": item.get("name", ""),
                        "version": item.get("version", ""),
                        "description": item.get("summary", "")
                    })
        except (json.JSONDecodeError, KeyError):
            # fallback: try simple package name check
            # if query looks like a package name, try fetching it
            if query.replace("_", "").replace("-", "").isalnum():
                if self.package_exists(query):
                    pkg = self.fetch_latest(query)
                    if pkg:
                        results.append({
                            "name": pkg.name,
                            "version": pkg.version,
                            "description": ""
                        })
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "releases" in data and isinstance(data["releases"], dict):
                # directly extract version keys from releases object
                for version in data["releases"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in pypi"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        # verify it's valid json with expected structure
        try:
            data = json.loads(metadata)
            return "info" in data and "releases" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse pypi json response"""
        try:
            data = json.loads(json_str)
            
            if "info" not in data:
                return None
            
            package = Package(name, version, "python")
            package.source = "PyPI"
            
            # extract dependencies
            deps = self._extract_dependencies(json_str, version)
            package.dependencies = deps
            
            # try to get checksum from releases
            if "releases" in data and version in data["releases"]:
                releases = data["releases"][version]
                if releases and len(releases) > 0:
                    # get first release (usually source distribution)
                    release = releases[0]
                    if "digests" in release and "sha256" in release["digests"]:
                        package.integrity = Integrity.format_integrity(release["digests"]["sha256"])
            
            return package
        except json.JSONDecodeError:
            return None
    
    def _extract_dependencies(self, json_str: str, version: str) -> List[Dependency]:
        """extract dependencies from pypi metadata"""
        deps = []
        
        try:
            data = json.loads(json_str)
            
            if ("info" in data and 
                "requires_dist" in data["info"] and 
                data["info"]["requires_dist"] is not None):
                
                for dep_str in data["info"]["requires_dist"]:
                    if isinstance(dep_str, str):
                        # skip optional dependencies (those with "extra" markers)
                        if "extra ==" in dep_str:
                            continue
                        
                        # parse dependency string (e.g., "numpy>=1.0.0")
                        # remove any markers after semicolon
                        if ';' in dep_str:
                            dep_str = dep_str.split(';')[0]
                        
                        dep_str = dep_str.strip()
                        
                        if dep_str:
                            try:
                                dep = Dependency.parse(dep_str)
                                deps.append(dep)
                            except Exception:
                                pass
        except (json.JSONDecodeError, KeyError):
            pass
        
        return deps
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}/json" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, response in zip(names, [results.get(url) for url in urls]):
            if response:
                cache_key = f"pypi:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)
                self._prefetch_cache[name] = response
            else:
                self._prefetch_cache[name] = None

"""

import json
import logging
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package
from ..core.dependency import Dependency
from ..core.validation import sanitize_package_name, ValidationError
from ..network.http_client import HttpClient
from ..network.cache import Cache
from ..installer.integrity import Integrity

logger = logging.getLogger(__name__)


class PyPISource(Source):
    """for getting python packages from pypi.org"""
    
    API_BASE_URL = "https://pypi.org/pypi/"
    SEARCH_URL = "https://pypi.org/search/"
    
    def __init__(self, cache: Optional[Cache] = None, base_url: Optional[str] = None, auth: Optional[Dict[str, str]] = None):
        self.http_client = HttpClient(auth=auth)
        self.cache = cache
        self._prefetch_cache: Dict[str, Optional[str]] = {}
        if base_url:
            self.API_BASE_URL = base_url
    
    def get_language(self) -> str:
        return "python"
    
    def get_name(self) -> str:
        return "PyPI"
    
    def _fetch_package_metadata(self, name: str) -> Optional[str]:
        """fetch package metadata from pypi"""
        # sanitize package name
        try:
            name = sanitize_package_name(name)
        except ValidationError as e:
            logger.error(f"Invalid package name: {e}")
            return None
        
        cache_key = f"pypi:{name}"
        
        # check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {name}")
                return cached
        
        # fetch from pypi
        url = f"{self.API_BASE_URL}{name}/json"
        logger.debug(f"Fetching {url}")
        response = self.http_client.get(url)
        
        if response:
            # validate response is valid JSON
            try:
                json.loads(response)  # validate it's JSON
                # cache the response
                if self.cache:
                    self.cache.set(cache_key, response)
                logger.debug(f"Successfully fetched and cached {name}")
                return response
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for {name}: {e}")
                return None
        else:
            logger.warning(f"Failed to fetch metadata for {name} from {url}")
        
        return None
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """search for packages on pypi"""
        # PyPI search API endpoint
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        url = f"{self.API_BASE_URL}search/?q={encoded_query}"
        response = self.http_client.get(url)
        
        if not response:
            return []
        
        results = []
        try:
            data = json.loads(response)
            if "results" in data:
                for item in data["results"][:limit]:
                    results.append({
                        "name": item.get("name", ""),
                        "version": item.get("version", ""),
                        "description": item.get("summary", "")
                    })
        except (json.JSONDecodeError, KeyError):
            # fallback: try simple package name check
            # if query looks like a package name, try fetching it
            if query.replace("_", "").replace("-", "").isalnum():
                if self.package_exists(query):
                    pkg = self.fetch_latest(query)
                    if pkg:
                        results.append({
                            "name": pkg.name,
                            "version": pkg.version,
                            "description": ""
                        })
        
        return results
    
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return []
        
        versions = []
        try:
            data = json.loads(metadata)
            if "releases" in data and isinstance(data["releases"], dict):
                # directly extract version keys from releases object
                for version in data["releases"].keys():
                    versions.append(version)
        except (json.JSONDecodeError, KeyError):
            return []
        
        return versions
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists in pypi"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return False
        
        # verify it's valid json with expected structure
        try:
            data = json.loads(metadata)
            return "info" in data and "releases" in data
        except json.JSONDecodeError:
            return False
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        metadata = self._fetch_package_metadata(name)
        if not metadata:
            return None
        
        return self._parse_package_json(metadata, name, version)
    
    def _parse_package_json(self, json_str: str, name: str, version: str) -> Optional[Package]:
        """parse pypi json response"""
        try:
            data = json.loads(json_str)
            
            if "info" not in data:
                return None
            
            package = Package(name, version, "python")
            package.source = "PyPI"
            
            # extract dependencies
            deps = self._extract_dependencies(json_str, version)
            package.dependencies = deps
            
            # try to get checksum from releases
            if "releases" in data and version in data["releases"]:
                releases = data["releases"][version]
                if releases and len(releases) > 0:
                    # get first release (usually source distribution)
                    release = releases[0]
                    if "digests" in release and "sha256" in release["digests"]:
                        package.integrity = Integrity.format_integrity(release["digests"]["sha256"])
            
            return package
        except json.JSONDecodeError:
            return None
    
    def _extract_dependencies(self, json_str: str, version: str) -> List[Dependency]:
        """extract dependencies from pypi metadata"""
        deps = []
        
        try:
            data = json.loads(json_str)
            
            if ("info" in data and 
                "requires_dist" in data["info"] and 
                data["info"]["requires_dist"] is not None):
                
                for dep_str in data["info"]["requires_dist"]:
                    if isinstance(dep_str, str):
                        # skip optional dependencies (those with "extra" markers)
                        if "extra ==" in dep_str:
                            continue
                        
                        # parse dependency string (e.g., "numpy>=1.0.0")
                        # remove any markers after semicolon
                        if ';' in dep_str:
                            dep_str = dep_str.split(';')[0]
                        
                        dep_str = dep_str.strip()
                        
                        if dep_str:
                            try:
                                dep = Dependency.parse(dep_str)
                                deps.append(dep)
                            except Exception:
                                pass
        except (json.JSONDecodeError, KeyError):
            pass
        
        return deps
    
    def prefetch(self, names: List[str]):
        """fetch metadata for multiple packages in parallel"""
        urls = [f"{self.API_BASE_URL}{name}/json" for name in names]
        
        # use parallel fetching
        results = self.http_client.get_parallel(urls, max_concurrent=4)
        
        # cache results
        for name, response in zip(names, [results.get(url) for url in urls]):
            if response:
                cache_key = f"pypi:{name}"
                if self.cache:
                    self.cache.set(cache_key, response)
                self._prefetch_cache[name] = response
            else:
                self._prefetch_cache[name] = None
