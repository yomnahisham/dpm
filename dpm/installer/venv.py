"""
venv.py - virtual environment management
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, List


class VirtualEnv:
    """virtual environment management"""
    
    def __init__(self):
        self.env_path: Optional[Path] = None
    
    def create(self, name: str, path: Optional[str] = None) -> bool:
        """create a virtual environment"""
        if path:
            env_path = Path(path)
        else:
            env_path = Path(name)
        
        self.env_path = env_path
        
        # try python3 -m venv first
        try:
            result = subprocess.run(
                ["python3", "-m", "venv", str(env_path)],
                capture_output=True,
                check=False
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass
        
        # fallback to virtualenv
        try:
            result = subprocess.run(
                ["virtualenv", str(env_path)],
                capture_output=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def activate_script(self) -> Optional[str]:
        """get path to activation script"""
        if not self.env_path or not self.env_path.exists():
            return None
        
        # try bin/activate (Unix)
        activate = self.env_path / "bin" / "activate"
        if activate.exists():
            return str(activate)
        
        # try Scripts/activate (Windows)
        activate = self.env_path / "Scripts" / "activate"
        if activate.exists():
            return str(activate)
        
        return None
    
    def status(self) -> Optional[Dict[str, str]]:
        """get virtual environment status"""
        if not self.env_path or not self.env_path.exists():
            # check if we're in an active venv
            venv = os.environ.get("VIRTUAL_ENV")
            if venv:
                return {
                    "active": "true",
                    "path": venv
                }
            return None
        
        activate = self.activate_script()
        return {
            "active": "false",
            "path": str(self.env_path),
            "activate_script": activate or ""
        }
    
    def remove(self) -> bool:
        """remove virtual environment"""
        if not self.env_path or not self.env_path.exists():
            return False
        
        import shutil
        try:
            shutil.rmtree(self.env_path)
            self.env_path = None
            return True
        except Exception:
            return False
    
    def detect_environment(self) -> Optional[Dict[str, str]]:
        """detect active environment (conda, poetry, pipenv, venv)"""
        # check conda
        conda_env = os.environ.get("CONDA_DEFAULT_ENV")
        if conda_env:
            return {
                "type": "conda",
                "name": conda_env,
                "path": os.environ.get("CONDA_PREFIX", "")
            }
        
        # check poetry
        poetry_env = os.environ.get("VIRTUAL_ENV")
        if poetry_env and "poetry" in poetry_env.lower():
            return {
                "type": "poetry",
                "path": poetry_env
            }
        
        # check pipenv
        pipenv_env = os.environ.get("PIPENV_ACTIVE")
        if pipenv_env:
            return {
                "type": "pipenv",
                "path": os.environ.get("VIRTUAL_ENV", "")
            }
        
        # check venv
        venv_env = os.environ.get("VIRTUAL_ENV")
        if venv_env:
            return {
                "type": "venv",
                "path": venv_env
            }
        
        return None
    
    def use_environment(self, env_type: str, path: Optional[str] = None) -> bool:
        """use existing environment"""
        detected = self.detect_environment()
        
        if env_type == "auto" and detected:
            self.env_path = Path(detected["path"])
            return True
        
        if path:
            self.env_path = Path(path)
            return self.env_path.exists()
        
        return False

