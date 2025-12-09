"""
state.py - tracks currently installed packages
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class PackageState:
    """tracks currently installed packages"""
    
    def __init__(self, state_file: Optional[str] = None):
        if state_file:
            self.state_file = Path(state_file)
        else:
            # default to ~/.dpm/state.json
            home = Path.home()
            self.state_file = home / ".dpm" / "state.json"
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.installed_packages: Dict[str, str] = {}  # name -> version
        self._load()
    
    def _load(self):
        """load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.installed_packages = data.get("packages", {})
            except Exception:
                self.installed_packages = {}
    
    def _save(self):
        """save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"packages": self.installed_packages}, f, indent=2)
        except Exception:
            pass
    
    def add_package(self, name: str, version: str):
        """record that a package is installed"""
        self.installed_packages[name] = version
        self._save()
    
    def remove_package(self, name: str):
        """record that a package is uninstalled"""
        if name in self.installed_packages:
            del self.installed_packages[name]
            self._save()
    
    def is_installed(self, name: str) -> bool:
        """check if a package is installed"""
        return name in self.installed_packages
    
    def get_installed_version(self, name: str) -> Optional[str]:
        """get installed version of a package"""
        return self.installed_packages.get(name)
    
    def get_all_installed(self) -> Dict[str, str]:
        """get all installed packages"""
        return self.installed_packages.copy()


state.py - tracks currently installed packages
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class PackageState:
    """tracks currently installed packages"""
    
    def __init__(self, state_file: Optional[str] = None):
        if state_file:
            self.state_file = Path(state_file)
        else:
            # default to ~/.dpm/state.json
            home = Path.home()
            self.state_file = home / ".dpm" / "state.json"
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.installed_packages: Dict[str, str] = {}  # name -> version
        self._load()
    
    def _load(self):
        """load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.installed_packages = data.get("packages", {})
            except Exception:
                self.installed_packages = {}
    
    def _save(self):
        """save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"packages": self.installed_packages}, f, indent=2)
        except Exception:
            pass
    
    def add_package(self, name: str, version: str):
        """record that a package is installed"""
        self.installed_packages[name] = version
        self._save()
    
    def remove_package(self, name: str):
        """record that a package is uninstalled"""
        if name in self.installed_packages:
            del self.installed_packages[name]
            self._save()
    
    def is_installed(self, name: str) -> bool:
        """check if a package is installed"""
        return name in self.installed_packages
    
    def get_installed_version(self, name: str) -> Optional[str]:
        """get installed version of a package"""
        return self.installed_packages.get(name)
    
    def get_all_installed(self) -> Dict[str, str]:
        """get all installed packages"""
        return self.installed_packages.copy()


state.py - tracks currently installed packages
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class PackageState:
    """tracks currently installed packages"""
    
    def __init__(self, state_file: Optional[str] = None):
        if state_file:
            self.state_file = Path(state_file)
        else:
            # default to ~/.dpm/state.json
            home = Path.home()
            self.state_file = home / ".dpm" / "state.json"
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.installed_packages: Dict[str, str] = {}  # name -> version
        self._load()
    
    def _load(self):
        """load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.installed_packages = data.get("packages", {})
            except Exception:
                self.installed_packages = {}
    
    def _save(self):
        """save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"packages": self.installed_packages}, f, indent=2)
        except Exception:
            pass
    
    def add_package(self, name: str, version: str):
        """record that a package is installed"""
        self.installed_packages[name] = version
        self._save()
    
    def remove_package(self, name: str):
        """record that a package is uninstalled"""
        if name in self.installed_packages:
            del self.installed_packages[name]
            self._save()
    
    def is_installed(self, name: str) -> bool:
        """check if a package is installed"""
        return name in self.installed_packages
    
    def get_installed_version(self, name: str) -> Optional[str]:
        """get installed version of a package"""
        return self.installed_packages.get(name)
    
    def get_all_installed(self) -> Dict[str, str]:
        """get all installed packages"""
        return self.installed_packages.copy()


state.py - tracks currently installed packages
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class PackageState:
    """tracks currently installed packages"""
    
    def __init__(self, state_file: Optional[str] = None):
        if state_file:
            self.state_file = Path(state_file)
        else:
            # default to ~/.dpm/state.json
            home = Path.home()
            self.state_file = home / ".dpm" / "state.json"
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.installed_packages: Dict[str, str] = {}  # name -> version
        self._load()
    
    def _load(self):
        """load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.installed_packages = data.get("packages", {})
            except Exception:
                self.installed_packages = {}
    
    def _save(self):
        """save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"packages": self.installed_packages}, f, indent=2)
        except Exception:
            pass
    
    def add_package(self, name: str, version: str):
        """record that a package is installed"""
        self.installed_packages[name] = version
        self._save()
    
    def remove_package(self, name: str):
        """record that a package is uninstalled"""
        if name in self.installed_packages:
            del self.installed_packages[name]
            self._save()
    
    def is_installed(self, name: str) -> bool:
        """check if a package is installed"""
        return name in self.installed_packages
    
    def get_installed_version(self, name: str) -> Optional[str]:
        """get installed version of a package"""
        return self.installed_packages.get(name)
    
    def get_all_installed(self) -> Dict[str, str]:
        """get all installed packages"""
        return self.installed_packages.copy()




