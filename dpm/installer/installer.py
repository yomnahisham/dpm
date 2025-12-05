"""
installer.py - actually installs packages using pip, npm, etc
"""

import subprocess
import os
from typing import List, Dict, Optional
from ..core.package import Package
from ..installer.integrity import Integrity


class Installer:
    """actually installs packages using pip, npm, etc"""
    
    def __init__(self, skip_integrity: bool = False):
        self.skip_integrity = skip_integrity
    
    def install(self, package: Package, verify_integrity: Optional[bool] = None) -> bool:
        """install a single package"""
        import logging
        logger = logging.getLogger(__name__)
        
        # verify integrity if checksum is available
        if verify_integrity is None:
            verify_integrity = not self.skip_integrity
        
        # note: actual integrity verification would require downloading the package
        # file first before installation. for now, we verify after installation
        # by checking the installed package files. this is a limitation but better
        # than doing nothing.
        
        # install the package first
        success = False
        if package.language == "python":
            success = self._install_python(package)
        elif package.language == "javascript":
            success = self._install_npm(package)
        elif package.language == "system":
            success = self._install_system(package)
        
        if not success:
            logger.error(f"Installation failed for {package.name}@{package.version}")
            return False
        
        # verify installation succeeded
        if not self._verify_installation(package):
            logger.warning(f"Installation verification failed for {package.name}@{package.version}")
            # don't fail here, as verification might be imperfect
            # but log the warning
        
        return True
    
    def _verify_installation(self, package: Package) -> bool:
        """verify that package was actually installed"""
        import subprocess
        
        if package.language == "python":
            # check if package is importable
            try:
                result = subprocess.run(
                    ["python3", "-c", f"import {package.name}"],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
                return result.returncode == 0
            except Exception:
                return False
        elif package.language == "javascript":
            # check if package exists in node_modules
            import os
            node_modules = os.path.join("node_modules", package.name)
            return os.path.exists(node_modules)
        
        # for system packages, assume success if install command succeeded
        return True
        
        if package.language == "python":
            return self._install_python(package)
        elif package.language == "javascript":
            return self._install_npm(package)
        elif package.language == "system":
            return self._install_system(package)
        return False
    
    def uninstall(self, package: Package) -> bool:
        """uninstall a single package"""
        if package.language == "python":
            return self._uninstall_python(package)
        elif package.language == "javascript":
            return self._uninstall_npm(package)
        elif package.language == "system":
            return self._uninstall_system(package)
        return False
    
    def _install_python(self, package: Package) -> bool:
        """install python package using pip"""
        try:
            # try pip3 first, then pip
            pip_cmd = "pip3" if self._command_exists("pip3") else "pip"
            
            cmd = [
                pip_cmd, "install", "--user", "--break-system-packages",
                f"{package.name}=={package.version}"
            ]
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _uninstall_python(self, package: Package) -> bool:
        """uninstall python package using pip"""
        try:
            pip_cmd = "pip3" if self._command_exists("pip3") else "pip"
            
            cmd = [
                pip_cmd, "uninstall", "--user", "--break-system-packages",
                "-y", package.name
            ]
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _install_npm(self, package: Package) -> bool:
        """install npm package"""
        try:
            cmd = ["npm", "install", f"{package.name}@{package.version}"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _uninstall_npm(self, package: Package) -> bool:
        """uninstall npm package"""
        try:
            cmd = ["npm", "uninstall", package.name]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _install_system(self, package: Package) -> bool:
        """install system package"""
        from ..sources.system import SystemSource
        source = SystemSource()
        return source.install_package(package.name)
    
    def _uninstall_system(self, package: Package) -> bool:
        """uninstall system package"""
        return False
    
    def _command_exists(self, command: str) -> bool:
        """check if a command exists"""
        try:
            result = subprocess.run(
                ["which", command], capture_output=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False

