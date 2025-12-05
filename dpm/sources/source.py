"""
source.py - base class for all package sources (pypi, npm, etc)
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from ..core.package import Package


class Source(ABC):
    """base class for all package sources (pypi, npm, etc)"""
    
    @abstractmethod
    def get_language(self) -> str:
        """what language this source handles"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """name of this source"""
        pass
    
    @abstractmethod
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a specific package version"""
        pass
    
    @abstractmethod
    def get_available_versions(self, name: str) -> List[str]:
        """get all available versions for a package"""
        pass
    
    @abstractmethod
    def package_exists(self, name: str) -> bool:
        """check if a package exists in this source"""
        pass
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        """get the latest version of a package"""
        versions = self.get_available_versions(name)
        if not versions:
            return None
        
        # try to get latest stable version first
        from ..core.version import Version
        
        stable_versions = []
        for v_str in versions:
            try:
                v = Version(v_str)
                if v.is_stable():
                    stable_versions.append((v, v_str))
            except ValueError:
                continue
        
        if stable_versions:
            stable_versions.sort(reverse=True, key=lambda x: x[0])
            latest_version = stable_versions[0][1]
        else:
            # fallback to any version
            try:
                all_versions = [(Version(v_str), v_str) for v_str in versions]
                all_versions.sort(reverse=True, key=lambda x: x[0])
                latest_version = all_versions[0][1]
            except ValueError:
                latest_version = versions[0]
        
        return self.fetch_package(name, latest_version)
    
    def prefetch(self, names: List[str]):
        """try to get info for many packages at once (for speed)
        default implementation: fetch latest for each package in parallel using threads
        specific sources can override this for better performance (e.g., batch API calls)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # skip package_exists check for sources where it's expensive (like SystemSource)
        # just try to fetch directly - if it fails, that's ok
        # this avoids expensive subprocess calls for system package manager
        
        # use thread pool to fetch in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_name = {
                executor.submit(self.fetch_latest, name): name 
                for name in names
            }
            
            # wait for all to complete (results are cached internally by sources)
            for future in as_completed(future_to_name):
                try:
                    future.result()  # just wait for it to complete
                except Exception:
                    pass  # ignore errors during prefetch
    
    def fetch_latest_batch(self, names: List[str]) -> Dict[str, Optional[Package]]:
        """fetch latest version for multiple packages"""
        results = {}
        for name in names:
            results[name] = self.fetch_latest(name)
        return results
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for packages
        default implementation: try exact name match, then partial name matching
        specific sources should override this to use their search APIs
        """
        results = []
        query_lower = query.lower()
        
        # this is a fallback - sources like PyPI and npm should override with real search
        # but for local/system sources, we can try name matching
        
        # try exact match first
        if self.package_exists(query):
            pkg = self.fetch_latest(query)
            if pkg:
                results.append({
                    "name": pkg.name,
                    "version": pkg.version,
                    "description": f"Package from {self.get_name()}",
                    "source": self.get_name()
                })
        
        # note: for a real implementation, sources should override this
        # to use their search APIs (like PyPI search endpoint, npm search, etc)
        # this default is just a fallback for sources without search APIs
        
        return results[:limit]

