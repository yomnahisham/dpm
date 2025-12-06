"""
exporter.py - export dependencies to various formats
"""

from typing import Dict, List
from pathlib import Path
from .manifest import Manifest
from ..installer.lockfile import LockFile


class Exporter:
    """export dependencies to various formats"""
    
    def __init__(self, manifest: Manifest = None, lockfile: LockFile = None):
        self.manifest = manifest or Manifest()
        self.lockfile = lockfile or LockFile()
    
    def export_requirements_txt(self, output_path: str = "requirements.txt") -> bool:
        """export to pip requirements.txt format"""
        try:
            # prefer lock file if available, otherwise use manifest
            if self.lockfile.exists():
                locked_versions = self.lockfile.get_locked_versions()
                lines = [f"{name}=={version}" for name, version in sorted(locked_versions.items())]
            elif self.manifest.exists():
                deps = self.manifest.get_dependencies()
                lines = [f"{name}{version}" for name, version in sorted(deps.items())]
            else:
                return False
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            
            return True
        except Exception:
            return False
    
    def export_package_json(self, output_path: str = "package.json") -> bool:
        """export to npm package.json format"""
        try:
            if not self.manifest.exists():
                return False
            
            manifest_data = self.manifest.read()
            if not manifest_data:
                return False
            
            # create package.json structure
            package_json = {
                "name": manifest_data.get("name", "my-project"),
                "version": manifest_data.get("version", "1.0.0"),
                "description": manifest_data.get("description", ""),
                "dependencies": {}
            }
            
            # convert dependencies
            deps = self.manifest.get_dependencies()
            for name, version in deps.items():
                # convert dpm version format to npm format
                # ==1.2.3 -> 1.2.3, ^1.2.3 -> ^1.2.3, etc
                npm_version = version
                if npm_version.startswith("=="):
                    npm_version = npm_version[2:]
                package_json["dependencies"][name] = npm_version
            
            import json
            with open(output_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def export_lock(self, output_path: str = "dpm.lock") -> bool:
        """export current lock file"""
        if not self.lockfile.exists():
            return False
        
        try:
            lock_data = self.lockfile.read()
            if not lock_data:
                return False
            
            import json
            with open(output_path, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            return True
        except Exception:
            return False


exporter.py - export dependencies to various formats
"""

from typing import Dict, List
from pathlib import Path
from .manifest import Manifest
from ..installer.lockfile import LockFile


class Exporter:
    """export dependencies to various formats"""
    
    def __init__(self, manifest: Manifest = None, lockfile: LockFile = None):
        self.manifest = manifest or Manifest()
        self.lockfile = lockfile or LockFile()
    
    def export_requirements_txt(self, output_path: str = "requirements.txt") -> bool:
        """export to pip requirements.txt format"""
        try:
            # prefer lock file if available, otherwise use manifest
            if self.lockfile.exists():
                locked_versions = self.lockfile.get_locked_versions()
                lines = [f"{name}=={version}" for name, version in sorted(locked_versions.items())]
            elif self.manifest.exists():
                deps = self.manifest.get_dependencies()
                lines = [f"{name}{version}" for name, version in sorted(deps.items())]
            else:
                return False
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            
            return True
        except Exception:
            return False
    
    def export_package_json(self, output_path: str = "package.json") -> bool:
        """export to npm package.json format"""
        try:
            if not self.manifest.exists():
                return False
            
            manifest_data = self.manifest.read()
            if not manifest_data:
                return False
            
            # create package.json structure
            package_json = {
                "name": manifest_data.get("name", "my-project"),
                "version": manifest_data.get("version", "1.0.0"),
                "description": manifest_data.get("description", ""),
                "dependencies": {}
            }
            
            # convert dependencies
            deps = self.manifest.get_dependencies()
            for name, version in deps.items():
                # convert dpm version format to npm format
                # ==1.2.3 -> 1.2.3, ^1.2.3 -> ^1.2.3, etc
                npm_version = version
                if npm_version.startswith("=="):
                    npm_version = npm_version[2:]
                package_json["dependencies"][name] = npm_version
            
            import json
            with open(output_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def export_lock(self, output_path: str = "dpm.lock") -> bool:
        """export current lock file"""
        if not self.lockfile.exists():
            return False
        
        try:
            lock_data = self.lockfile.read()
            if not lock_data:
                return False
            
            import json
            with open(output_path, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            return True
        except Exception:
            return False


exporter.py - export dependencies to various formats
"""

from typing import Dict, List
from pathlib import Path
from .manifest import Manifest
from ..installer.lockfile import LockFile


class Exporter:
    """export dependencies to various formats"""
    
    def __init__(self, manifest: Manifest = None, lockfile: LockFile = None):
        self.manifest = manifest or Manifest()
        self.lockfile = lockfile or LockFile()
    
    def export_requirements_txt(self, output_path: str = "requirements.txt") -> bool:
        """export to pip requirements.txt format"""
        try:
            # prefer lock file if available, otherwise use manifest
            if self.lockfile.exists():
                locked_versions = self.lockfile.get_locked_versions()
                lines = [f"{name}=={version}" for name, version in sorted(locked_versions.items())]
            elif self.manifest.exists():
                deps = self.manifest.get_dependencies()
                lines = [f"{name}{version}" for name, version in sorted(deps.items())]
            else:
                return False
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            
            return True
        except Exception:
            return False
    
    def export_package_json(self, output_path: str = "package.json") -> bool:
        """export to npm package.json format"""
        try:
            if not self.manifest.exists():
                return False
            
            manifest_data = self.manifest.read()
            if not manifest_data:
                return False
            
            # create package.json structure
            package_json = {
                "name": manifest_data.get("name", "my-project"),
                "version": manifest_data.get("version", "1.0.0"),
                "description": manifest_data.get("description", ""),
                "dependencies": {}
            }
            
            # convert dependencies
            deps = self.manifest.get_dependencies()
            for name, version in deps.items():
                # convert dpm version format to npm format
                # ==1.2.3 -> 1.2.3, ^1.2.3 -> ^1.2.3, etc
                npm_version = version
                if npm_version.startswith("=="):
                    npm_version = npm_version[2:]
                package_json["dependencies"][name] = npm_version
            
            import json
            with open(output_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def export_lock(self, output_path: str = "dpm.lock") -> bool:
        """export current lock file"""
        if not self.lockfile.exists():
            return False
        
        try:
            lock_data = self.lockfile.read()
            if not lock_data:
                return False
            
            import json
            with open(output_path, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            return True
        except Exception:
            return False


exporter.py - export dependencies to various formats
"""

from typing import Dict, List
from pathlib import Path
from .manifest import Manifest
from ..installer.lockfile import LockFile


class Exporter:
    """export dependencies to various formats"""
    
    def __init__(self, manifest: Manifest = None, lockfile: LockFile = None):
        self.manifest = manifest or Manifest()
        self.lockfile = lockfile or LockFile()
    
    def export_requirements_txt(self, output_path: str = "requirements.txt") -> bool:
        """export to pip requirements.txt format"""
        try:
            # prefer lock file if available, otherwise use manifest
            if self.lockfile.exists():
                locked_versions = self.lockfile.get_locked_versions()
                lines = [f"{name}=={version}" for name, version in sorted(locked_versions.items())]
            elif self.manifest.exists():
                deps = self.manifest.get_dependencies()
                lines = [f"{name}{version}" for name, version in sorted(deps.items())]
            else:
                return False
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            
            return True
        except Exception:
            return False
    
    def export_package_json(self, output_path: str = "package.json") -> bool:
        """export to npm package.json format"""
        try:
            if not self.manifest.exists():
                return False
            
            manifest_data = self.manifest.read()
            if not manifest_data:
                return False
            
            # create package.json structure
            package_json = {
                "name": manifest_data.get("name", "my-project"),
                "version": manifest_data.get("version", "1.0.0"),
                "description": manifest_data.get("description", ""),
                "dependencies": {}
            }
            
            # convert dependencies
            deps = self.manifest.get_dependencies()
            for name, version in deps.items():
                # convert dpm version format to npm format
                # ==1.2.3 -> 1.2.3, ^1.2.3 -> ^1.2.3, etc
                npm_version = version
                if npm_version.startswith("=="):
                    npm_version = npm_version[2:]
                package_json["dependencies"][name] = npm_version
            
            import json
            with open(output_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def export_lock(self, output_path: str = "dpm.lock") -> bool:
        """export current lock file"""
        if not self.lockfile.exists():
            return False
        
        try:
            lock_data = self.lockfile.read()
            if not lock_data:
                return False
            
            import json
            with open(output_path, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            return True
        except Exception:
            return False


