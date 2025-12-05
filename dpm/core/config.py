"""
config.py - configuration file management
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any


class Config:
    """configuration file management"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # default to ~/.dpm/config.json
            home = Path.home()
            self.config_path = home / ".dpm" / "config.json"
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        """load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
            except Exception:
                self._config = {}
        else:
            # create default config
            self._config = self._default_config()
            self._save()
    
    def _default_config(self) -> Dict[str, Any]:
        """default configuration values"""
        return {
            "cache_dir": str(Path.home() / ".dpm" / "cache"),
            "default_sources": ["pypi", "npm"],
            "timeout": 30,
            "max_workers": 4,
            "log_level": "INFO",
            "log_file": str(Path.home() / ".dpm" / "dpm.log")
        }
    
    def _save(self):
        """save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """set configuration value"""
        self._config[key] = value
        self._save()
    
    def get_cache_dir(self) -> str:
        """get cache directory"""
        return self.get("cache_dir", str(Path.home() / ".dpm" / "cache"))
    
    def get_default_sources(self) -> list:
        """get default sources"""
        return self.get("default_sources", ["pypi", "npm"])
    
    def get_timeout(self) -> int:
        """get network timeout"""
        return self.get("timeout", 30)
    
    def get_max_workers(self) -> int:
        """get max parallel workers"""
        return self.get("max_workers", 4)
    
    def get_log_level(self) -> str:
        """get log level"""
        return self.get("log_level", "INFO")
    
    def get_log_file(self) -> str:
        """get log file path"""
        return self.get("log_file", str(Path.home() / ".dpm" / "dpm.log"))

