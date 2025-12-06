"""
custom_repo.py - custom repository source wrapper
"""

import logging
from typing import Optional, List, Dict
from .source import Source
from .pypi import PyPISource
from .npm import NpmSource
from ..core.package import Package
from ..core.repository import Repository
from ..network.cache import Cache

logger = logging.getLogger(__name__)


class CustomRepositorySource(Source):
    """wrapper source that uses a custom repository URL"""
    
    def __init__(self, repository: Repository, cache: Optional[Cache] = None):
        self.repository = repository
        self.cache = cache
        self._wrapped_source: Optional[Source] = None
        self._detect_source_type()
    
    def _detect_source_type(self):
        """detect if this is a PyPI or npm repository based on URL"""
        url = self.repository.url.lower()
        
        # check if it looks like a PyPI repository
        if 'pypi' in url or url.endswith('/pypi') or '/simple' in url:
            self._wrapped_source = PyPISource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected PyPI repository: {self.repository.name}")
            return
        
        # check if it looks like an npm repository
        if 'npm' in url or 'registry' in url:
            self._wrapped_source = NpmSource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'npm')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected npm repository: {self.repository.name}")
            return
        
        # default to PyPI if we can't tell
        logger.warning(f"Could not detect repository type for {self.repository.url}, defaulting to PyPI")
        self._wrapped_source = PyPISource(self.cache)
        self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
        if hasattr(self._wrapped_source, 'http_client'):
            self._wrapped_source.http_client.auth = self.repository.auth
    
    def _normalize_url(self, url: str, repo_type: str) -> str:
        """normalize repository URL to proper format"""
        url = url.rstrip('/')
        
        if repo_type == 'pypi':
            # PyPI format: https://pypi.org/pypi/ or https://pypi.company.com/pypi/
            if not url.endswith('/pypi'):
                if url.endswith('/'):
                    url = url + 'pypi'
                else:
                    url = url + '/pypi'
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        elif repo_type == 'npm':
            # npm format: https://registry.npmjs.org/ or https://npm.company.com/
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        return url
    
    def get_language(self) -> str:
        if self._wrapped_source:
            return self._wrapped_source.get_language()
        return "unknown"
    
    def get_name(self) -> str:
        return f"Custom ({self.repository.name})"
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_package(name, version)
        return None
    
    def get_available_versions(self, name: str) -> List[str]:
        if self._wrapped_source:
            return self._wrapped_source.get_available_versions(name)
        return []
    
    def package_exists(self, name: str) -> bool:
        if self._wrapped_source:
            return self._wrapped_source.package_exists(name)
        return False
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_latest(name)
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        if self._wrapped_source:
            results = self._wrapped_source.search(query, limit)
            # update source name in results
            for result in results:
                result["source"] = self.get_name()
            return results
        return []
    
    def prefetch(self, names: List[str]):
        if self._wrapped_source:
            self._wrapped_source.prefetch(names)


custom_repo.py - custom repository source wrapper
"""

import logging
from typing import Optional, List, Dict
from .source import Source
from .pypi import PyPISource
from .npm import NpmSource
from ..core.package import Package
from ..core.repository import Repository
from ..network.cache import Cache

logger = logging.getLogger(__name__)


class CustomRepositorySource(Source):
    """wrapper source that uses a custom repository URL"""
    
    def __init__(self, repository: Repository, cache: Optional[Cache] = None):
        self.repository = repository
        self.cache = cache
        self._wrapped_source: Optional[Source] = None
        self._detect_source_type()
    
    def _detect_source_type(self):
        """detect if this is a PyPI or npm repository based on URL"""
        url = self.repository.url.lower()
        
        # check if it looks like a PyPI repository
        if 'pypi' in url or url.endswith('/pypi') or '/simple' in url:
            self._wrapped_source = PyPISource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected PyPI repository: {self.repository.name}")
            return
        
        # check if it looks like an npm repository
        if 'npm' in url or 'registry' in url:
            self._wrapped_source = NpmSource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'npm')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected npm repository: {self.repository.name}")
            return
        
        # default to PyPI if we can't tell
        logger.warning(f"Could not detect repository type for {self.repository.url}, defaulting to PyPI")
        self._wrapped_source = PyPISource(self.cache)
        self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
        if hasattr(self._wrapped_source, 'http_client'):
            self._wrapped_source.http_client.auth = self.repository.auth
    
    def _normalize_url(self, url: str, repo_type: str) -> str:
        """normalize repository URL to proper format"""
        url = url.rstrip('/')
        
        if repo_type == 'pypi':
            # PyPI format: https://pypi.org/pypi/ or https://pypi.company.com/pypi/
            if not url.endswith('/pypi'):
                if url.endswith('/'):
                    url = url + 'pypi'
                else:
                    url = url + '/pypi'
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        elif repo_type == 'npm':
            # npm format: https://registry.npmjs.org/ or https://npm.company.com/
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        return url
    
    def get_language(self) -> str:
        if self._wrapped_source:
            return self._wrapped_source.get_language()
        return "unknown"
    
    def get_name(self) -> str:
        return f"Custom ({self.repository.name})"
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_package(name, version)
        return None
    
    def get_available_versions(self, name: str) -> List[str]:
        if self._wrapped_source:
            return self._wrapped_source.get_available_versions(name)
        return []
    
    def package_exists(self, name: str) -> bool:
        if self._wrapped_source:
            return self._wrapped_source.package_exists(name)
        return False
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_latest(name)
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        if self._wrapped_source:
            results = self._wrapped_source.search(query, limit)
            # update source name in results
            for result in results:
                result["source"] = self.get_name()
            return results
        return []
    
    def prefetch(self, names: List[str]):
        if self._wrapped_source:
            self._wrapped_source.prefetch(names)


custom_repo.py - custom repository source wrapper
"""

import logging
from typing import Optional, List, Dict
from .source import Source
from .pypi import PyPISource
from .npm import NpmSource
from ..core.package import Package
from ..core.repository import Repository
from ..network.cache import Cache

logger = logging.getLogger(__name__)


class CustomRepositorySource(Source):
    """wrapper source that uses a custom repository URL"""
    
    def __init__(self, repository: Repository, cache: Optional[Cache] = None):
        self.repository = repository
        self.cache = cache
        self._wrapped_source: Optional[Source] = None
        self._detect_source_type()
    
    def _detect_source_type(self):
        """detect if this is a PyPI or npm repository based on URL"""
        url = self.repository.url.lower()
        
        # check if it looks like a PyPI repository
        if 'pypi' in url or url.endswith('/pypi') or '/simple' in url:
            self._wrapped_source = PyPISource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected PyPI repository: {self.repository.name}")
            return
        
        # check if it looks like an npm repository
        if 'npm' in url or 'registry' in url:
            self._wrapped_source = NpmSource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'npm')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected npm repository: {self.repository.name}")
            return
        
        # default to PyPI if we can't tell
        logger.warning(f"Could not detect repository type for {self.repository.url}, defaulting to PyPI")
        self._wrapped_source = PyPISource(self.cache)
        self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
        if hasattr(self._wrapped_source, 'http_client'):
            self._wrapped_source.http_client.auth = self.repository.auth
    
    def _normalize_url(self, url: str, repo_type: str) -> str:
        """normalize repository URL to proper format"""
        url = url.rstrip('/')
        
        if repo_type == 'pypi':
            # PyPI format: https://pypi.org/pypi/ or https://pypi.company.com/pypi/
            if not url.endswith('/pypi'):
                if url.endswith('/'):
                    url = url + 'pypi'
                else:
                    url = url + '/pypi'
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        elif repo_type == 'npm':
            # npm format: https://registry.npmjs.org/ or https://npm.company.com/
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        return url
    
    def get_language(self) -> str:
        if self._wrapped_source:
            return self._wrapped_source.get_language()
        return "unknown"
    
    def get_name(self) -> str:
        return f"Custom ({self.repository.name})"
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_package(name, version)
        return None
    
    def get_available_versions(self, name: str) -> List[str]:
        if self._wrapped_source:
            return self._wrapped_source.get_available_versions(name)
        return []
    
    def package_exists(self, name: str) -> bool:
        if self._wrapped_source:
            return self._wrapped_source.package_exists(name)
        return False
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_latest(name)
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        if self._wrapped_source:
            results = self._wrapped_source.search(query, limit)
            # update source name in results
            for result in results:
                result["source"] = self.get_name()
            return results
        return []
    
    def prefetch(self, names: List[str]):
        if self._wrapped_source:
            self._wrapped_source.prefetch(names)


custom_repo.py - custom repository source wrapper
"""

import logging
from typing import Optional, List, Dict
from .source import Source
from .pypi import PyPISource
from .npm import NpmSource
from ..core.package import Package
from ..core.repository import Repository
from ..network.cache import Cache

logger = logging.getLogger(__name__)


class CustomRepositorySource(Source):
    """wrapper source that uses a custom repository URL"""
    
    def __init__(self, repository: Repository, cache: Optional[Cache] = None):
        self.repository = repository
        self.cache = cache
        self._wrapped_source: Optional[Source] = None
        self._detect_source_type()
    
    def _detect_source_type(self):
        """detect if this is a PyPI or npm repository based on URL"""
        url = self.repository.url.lower()
        
        # check if it looks like a PyPI repository
        if 'pypi' in url or url.endswith('/pypi') or '/simple' in url:
            self._wrapped_source = PyPISource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected PyPI repository: {self.repository.name}")
            return
        
        # check if it looks like an npm repository
        if 'npm' in url or 'registry' in url:
            self._wrapped_source = NpmSource(self.cache)
            self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'npm')
            if hasattr(self._wrapped_source, 'http_client'):
                self._wrapped_source.http_client.auth = self.repository.auth
            logger.info(f"Detected npm repository: {self.repository.name}")
            return
        
        # default to PyPI if we can't tell
        logger.warning(f"Could not detect repository type for {self.repository.url}, defaulting to PyPI")
        self._wrapped_source = PyPISource(self.cache)
        self._wrapped_source.API_BASE_URL = self._normalize_url(self.repository.url, 'pypi')
        if hasattr(self._wrapped_source, 'http_client'):
            self._wrapped_source.http_client.auth = self.repository.auth
    
    def _normalize_url(self, url: str, repo_type: str) -> str:
        """normalize repository URL to proper format"""
        url = url.rstrip('/')
        
        if repo_type == 'pypi':
            # PyPI format: https://pypi.org/pypi/ or https://pypi.company.com/pypi/
            if not url.endswith('/pypi'):
                if url.endswith('/'):
                    url = url + 'pypi'
                else:
                    url = url + '/pypi'
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        elif repo_type == 'npm':
            # npm format: https://registry.npmjs.org/ or https://npm.company.com/
            if not url.endswith('/'):
                url = url + '/'
            return url
        
        return url
    
    def get_language(self) -> str:
        if self._wrapped_source:
            return self._wrapped_source.get_language()
        return "unknown"
    
    def get_name(self) -> str:
        return f"Custom ({self.repository.name})"
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_package(name, version)
        return None
    
    def get_available_versions(self, name: str) -> List[str]:
        if self._wrapped_source:
            return self._wrapped_source.get_available_versions(name)
        return []
    
    def package_exists(self, name: str) -> bool:
        if self._wrapped_source:
            return self._wrapped_source.package_exists(name)
        return False
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        if self._wrapped_source:
            return self._wrapped_source.fetch_latest(name)
        return None
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        if self._wrapped_source:
            results = self._wrapped_source.search(query, limit)
            # update source name in results
            for result in results:
                result["source"] = self.get_name()
            return results
        return []
    
    def prefetch(self, names: List[str]):
        if self._wrapped_source:
            self._wrapped_source.prefetch(names)



