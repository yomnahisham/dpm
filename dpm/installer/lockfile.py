"""
lockfile.py - for reading and writing dpm.lock files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class LockFile:
    """for reading and writing dpm.lock files"""
    
    def __init__(self, lockfile_path: str = "dpm.lock"):
        self.lockfile_path = Path(lockfile_path)
    
    def exists(self) -> bool:
        """check if lock file exists"""
        return self.lockfile_path.exists()
    
    def read(self) -> Optional[Dict]:
        """read lock file"""
        if not self.exists():
            return None
        
        try:
            with open(self.lockfile_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def write(self, selected_versions: Dict[str, str],
              dependency_map: Dict[str, List[str]],
              package_info: Dict[str, Dict[str, str]]):
        """write lock file with resolved versions"""
        lock_data = {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "packages": {}
        }
        
        for name, version in selected_versions.items():
            info = package_info.get(name, {})
            lock_data["packages"][name] = {
                "version": version,
                "language": info.get("language", "unknown"),
                "source": info.get("source", "unknown"),
                "dependencies": dependency_map.get(name, []),
                "integrity": info.get("integrity")
            }
        
        try:
            # write atomically: write to temp file first, then rename
            import tempfile
            temp_file = self.lockfile_path.with_suffix('.tmp')
            try:
                with open(temp_file, 'w') as f:
                    json.dump(lock_data, f, indent=2)
                # atomic rename
                temp_file.replace(self.lockfile_path)
                return True
            except Exception as e:
                # cleanup temp file on error
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to write lock file: {e}")
                return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to write lock file: {e}")
            return False
    
    def get_locked_versions(self) -> Dict[str, str]:
        """get locked versions from lock file"""
        lock_data = self.read()
        if not lock_data or "packages" not in lock_data:
            return {}
        
        versions = {}
        for name, pkg_data in lock_data["packages"].items():
            if isinstance(pkg_data, dict) and "version" in pkg_data:
                versions[name] = pkg_data["version"]
        
        return versions
    
    def get_locked_packages(self) -> List[str]:
        """get list of locked package names"""
        lock_data = self.read()
        if not lock_data or "packages" not in lock_data:
            return []
        
        return list(lock_data["packages"].keys())

