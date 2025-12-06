"""
system.py - for system packages (apt, yum, etc)
"""

import subprocess
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package


class SystemSource(Source):
    """for system packages (apt, yum, etc)"""
    
    def __init__(self):
        self.package_manager = self._detect_package_manager()
        self._package_cache: Dict[str, bool] = {}  # cache package_exists results
    
    def _detect_package_manager(self) -> str:
        """detect which package manager is available"""
        if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
            return "apt"
        elif subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
            return "yum"
        elif subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
            return "brew"
        return "unknown"
    
    def get_language(self) -> str:
        return "system"
    
    def get_name(self) -> str:
        return f"System ({self.package_manager})"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists (with caching)"""
        # check cache first
        if name in self._package_cache:
            return self._package_cache[name]
        
        # for performance, skip system package checks for common package names
        # that are clearly not system packages (python/js packages)
        # this avoids expensive subprocess calls
        if self.package_manager == "unknown":
            self._package_cache[name] = False
            return False
        
        # only check if it looks like a system package name
        # (system packages usually don't have underscores or dots in the middle)
        # this is a heuristic to avoid checking python packages like "requests" or "flask"
        if '_' in name or ('.' in name and not name.startswith('python')):
            # likely a python/js package, not a system package
            self._package_cache[name] = False
            return False
        
        result = False
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", "--names-only", f"^{name}$"],
                capture_output=True,
                timeout=2,  # timeout to prevent hanging
                check=False
            )
            result = result.returncode == 0 and result.stdout.strip() != b""
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "list", "available", name],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", "--formula", f"^{name}$"],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0 and name.encode() in result.stdout
        
        # cache the result
        self._package_cache[name] = result
        return result
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        # system packages usually don't have multiple versions
        return ["latest"]
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a system package"""
        package = Package(name, version or "latest", "system")
        package.source = self.package_manager
        # system packages typically don't have dependencies we can resolve
        package.dependencies = []
        return package
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        """get latest system package"""
        return self.fetch_package(name, "latest")
    
    def install_package(self, name: str) -> bool:
        """install a system package"""
        if self.package_manager == "apt":
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["sudo", "yum", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "install", name],
                check=False
            )
            return result.returncode == 0
        return False
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for system packages"""
        results = []
        
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    if ' - ' in line:
                        name, desc = line.split(' - ', 1)
                        name = name.strip()
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": desc.strip(),
                            "source": f"System ({self.package_manager})"
                        })
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                # parse yum search output (simplified)
                for line in result.stdout.split('\n')[:limit]:
                    if line.strip() and not line.startswith('='):
                        parts = line.split()
                        if parts:
                            results.append({
                                "name": parts[0],
                                "version": "latest",
                                "description": " ".join(parts[1:]) if len(parts) > 1 else "",
                                "source": f"System ({self.package_manager})"
                            })
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    name = line.strip()
                    if name:
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": f"Homebrew formula",
                            "source": f"System ({self.package_manager})"
                        })
        
        return results[:limit]


"""

import subprocess
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package


class SystemSource(Source):
    """for system packages (apt, yum, etc)"""
    
    def __init__(self):
        self.package_manager = self._detect_package_manager()
        self._package_cache: Dict[str, bool] = {}  # cache package_exists results
    
    def _detect_package_manager(self) -> str:
        """detect which package manager is available"""
        if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
            return "apt"
        elif subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
            return "yum"
        elif subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
            return "brew"
        return "unknown"
    
    def get_language(self) -> str:
        return "system"
    
    def get_name(self) -> str:
        return f"System ({self.package_manager})"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists (with caching)"""
        # check cache first
        if name in self._package_cache:
            return self._package_cache[name]
        
        # for performance, skip system package checks for common package names
        # that are clearly not system packages (python/js packages)
        # this avoids expensive subprocess calls
        if self.package_manager == "unknown":
            self._package_cache[name] = False
            return False
        
        # only check if it looks like a system package name
        # (system packages usually don't have underscores or dots in the middle)
        # this is a heuristic to avoid checking python packages like "requests" or "flask"
        if '_' in name or ('.' in name and not name.startswith('python')):
            # likely a python/js package, not a system package
            self._package_cache[name] = False
            return False
        
        result = False
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", "--names-only", f"^{name}$"],
                capture_output=True,
                timeout=2,  # timeout to prevent hanging
                check=False
            )
            result = result.returncode == 0 and result.stdout.strip() != b""
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "list", "available", name],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", "--formula", f"^{name}$"],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0 and name.encode() in result.stdout
        
        # cache the result
        self._package_cache[name] = result
        return result
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        # system packages usually don't have multiple versions
        return ["latest"]
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a system package"""
        package = Package(name, version or "latest", "system")
        package.source = self.package_manager
        # system packages typically don't have dependencies we can resolve
        package.dependencies = []
        return package
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        """get latest system package"""
        return self.fetch_package(name, "latest")
    
    def install_package(self, name: str) -> bool:
        """install a system package"""
        if self.package_manager == "apt":
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["sudo", "yum", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "install", name],
                check=False
            )
            return result.returncode == 0
        return False
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for system packages"""
        results = []
        
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    if ' - ' in line:
                        name, desc = line.split(' - ', 1)
                        name = name.strip()
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": desc.strip(),
                            "source": f"System ({self.package_manager})"
                        })
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                # parse yum search output (simplified)
                for line in result.stdout.split('\n')[:limit]:
                    if line.strip() and not line.startswith('='):
                        parts = line.split()
                        if parts:
                            results.append({
                                "name": parts[0],
                                "version": "latest",
                                "description": " ".join(parts[1:]) if len(parts) > 1 else "",
                                "source": f"System ({self.package_manager})"
                            })
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    name = line.strip()
                    if name:
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": f"Homebrew formula",
                            "source": f"System ({self.package_manager})"
                        })
        
        return results[:limit]


"""

import subprocess
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package


class SystemSource(Source):
    """for system packages (apt, yum, etc)"""
    
    def __init__(self):
        self.package_manager = self._detect_package_manager()
        self._package_cache: Dict[str, bool] = {}  # cache package_exists results
    
    def _detect_package_manager(self) -> str:
        """detect which package manager is available"""
        if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
            return "apt"
        elif subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
            return "yum"
        elif subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
            return "brew"
        return "unknown"
    
    def get_language(self) -> str:
        return "system"
    
    def get_name(self) -> str:
        return f"System ({self.package_manager})"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists (with caching)"""
        # check cache first
        if name in self._package_cache:
            return self._package_cache[name]
        
        # for performance, skip system package checks for common package names
        # that are clearly not system packages (python/js packages)
        # this avoids expensive subprocess calls
        if self.package_manager == "unknown":
            self._package_cache[name] = False
            return False
        
        # only check if it looks like a system package name
        # (system packages usually don't have underscores or dots in the middle)
        # this is a heuristic to avoid checking python packages like "requests" or "flask"
        if '_' in name or ('.' in name and not name.startswith('python')):
            # likely a python/js package, not a system package
            self._package_cache[name] = False
            return False
        
        result = False
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", "--names-only", f"^{name}$"],
                capture_output=True,
                timeout=2,  # timeout to prevent hanging
                check=False
            )
            result = result.returncode == 0 and result.stdout.strip() != b""
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "list", "available", name],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", "--formula", f"^{name}$"],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0 and name.encode() in result.stdout
        
        # cache the result
        self._package_cache[name] = result
        return result
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        # system packages usually don't have multiple versions
        return ["latest"]
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a system package"""
        package = Package(name, version or "latest", "system")
        package.source = self.package_manager
        # system packages typically don't have dependencies we can resolve
        package.dependencies = []
        return package
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        """get latest system package"""
        return self.fetch_package(name, "latest")
    
    def install_package(self, name: str) -> bool:
        """install a system package"""
        if self.package_manager == "apt":
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["sudo", "yum", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "install", name],
                check=False
            )
            return result.returncode == 0
        return False
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for system packages"""
        results = []
        
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    if ' - ' in line:
                        name, desc = line.split(' - ', 1)
                        name = name.strip()
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": desc.strip(),
                            "source": f"System ({self.package_manager})"
                        })
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                # parse yum search output (simplified)
                for line in result.stdout.split('\n')[:limit]:
                    if line.strip() and not line.startswith('='):
                        parts = line.split()
                        if parts:
                            results.append({
                                "name": parts[0],
                                "version": "latest",
                                "description": " ".join(parts[1:]) if len(parts) > 1 else "",
                                "source": f"System ({self.package_manager})"
                            })
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    name = line.strip()
                    if name:
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": f"Homebrew formula",
                            "source": f"System ({self.package_manager})"
                        })
        
        return results[:limit]


"""

import subprocess
from typing import Optional, List, Dict
from .source import Source
from ..core.package import Package


class SystemSource(Source):
    """for system packages (apt, yum, etc)"""
    
    def __init__(self):
        self.package_manager = self._detect_package_manager()
        self._package_cache: Dict[str, bool] = {}  # cache package_exists results
    
    def _detect_package_manager(self) -> str:
        """detect which package manager is available"""
        if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
            return "apt"
        elif subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
            return "yum"
        elif subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
            return "brew"
        return "unknown"
    
    def get_language(self) -> str:
        return "system"
    
    def get_name(self) -> str:
        return f"System ({self.package_manager})"
    
    def package_exists(self, name: str) -> bool:
        """check if a package exists (with caching)"""
        # check cache first
        if name in self._package_cache:
            return self._package_cache[name]
        
        # for performance, skip system package checks for common package names
        # that are clearly not system packages (python/js packages)
        # this avoids expensive subprocess calls
        if self.package_manager == "unknown":
            self._package_cache[name] = False
            return False
        
        # only check if it looks like a system package name
        # (system packages usually don't have underscores or dots in the middle)
        # this is a heuristic to avoid checking python packages like "requests" or "flask"
        if '_' in name or ('.' in name and not name.startswith('python')):
            # likely a python/js package, not a system package
            self._package_cache[name] = False
            return False
        
        result = False
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", "--names-only", f"^{name}$"],
                capture_output=True,
                timeout=2,  # timeout to prevent hanging
                check=False
            )
            result = result.returncode == 0 and result.stdout.strip() != b""
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "list", "available", name],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", "--formula", f"^{name}$"],
                capture_output=True,
                timeout=2,
                check=False
            )
            result = result.returncode == 0 and name.encode() in result.stdout
        
        # cache the result
        self._package_cache[name] = result
        return result
    
    def get_available_versions(self, name: str) -> List[str]:
        """get available versions"""
        # system packages usually don't have multiple versions
        return ["latest"]
    
    def fetch_package(self, name: str, version: str) -> Optional[Package]:
        """get a system package"""
        package = Package(name, version or "latest", "system")
        package.source = self.package_manager
        # system packages typically don't have dependencies we can resolve
        package.dependencies = []
        return package
    
    def fetch_latest(self, name: str) -> Optional[Package]:
        """get latest system package"""
        return self.fetch_package(name, "latest")
    
    def install_package(self, name: str) -> bool:
        """install a system package"""
        if self.package_manager == "apt":
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["sudo", "yum", "install", "-y", name],
                check=False
            )
            return result.returncode == 0
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "install", name],
                check=False
            )
            return result.returncode == 0
        return False
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """search for system packages"""
        results = []
        
        if self.package_manager == "apt":
            result = subprocess.run(
                ["apt-cache", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    if ' - ' in line:
                        name, desc = line.split(' - ', 1)
                        name = name.strip()
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": desc.strip(),
                            "source": f"System ({self.package_manager})"
                        })
        elif self.package_manager == "yum":
            result = subprocess.run(
                ["yum", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                # parse yum search output (simplified)
                for line in result.stdout.split('\n')[:limit]:
                    if line.strip() and not line.startswith('='):
                        parts = line.split()
                        if parts:
                            results.append({
                                "name": parts[0],
                                "version": "latest",
                                "description": " ".join(parts[1:]) if len(parts) > 1 else "",
                                "source": f"System ({self.package_manager})"
                            })
        elif self.package_manager == "brew":
            result = subprocess.run(
                ["brew", "search", query],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:limit]:
                    name = line.strip()
                    if name:
                        results.append({
                            "name": name,
                            "version": "latest",
                            "description": f"Homebrew formula",
                            "source": f"System ({self.package_manager})"
                        })
        
        return results[:limit]

