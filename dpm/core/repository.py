"""
repository.py - repository management for custom package sources
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Repository:
    """repository configuration"""
    
    def __init__(self, name: str, url: str, auth: Optional[Dict[str, str]] = None):
        self.name = name
        self.url = url
        self.auth = auth or {}


class RepositoryManager:
    """manage custom repositories"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            home = Path.home()
            self.config_path = home / ".dpm" / "repositories.json"
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.repositories: Dict[str, Repository] = {}
        self._load()
    
    def _load(self):
        """load repositories from config"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for name, repo_data in data.get("repositories", {}).items():
                        self.repositories[name] = Repository(
                            name=name,
                            url=repo_data.get("url", ""),
                            auth=repo_data.get("auth")
                        )
            except Exception:
                self.repositories = {}
        else:
            self.repositories = {}
    
    def _save(self):
        """save repositories to config"""
        data = {
            "repositories": {}
        }
        for name, repo in self.repositories.items():
            data["repositories"][name] = {
                "url": repo.url,
                "auth": repo.auth
            }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def add(self, name: str, url: str, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """add a repository"""
        auth = None
        if username and password:
            auth = {"username": username, "password": password}
        
        repo = Repository(name, url, auth)
        self.repositories[name] = repo
        return self._save()
    
    def remove(self, name: str) -> bool:
        """remove a repository"""
        if name in self.repositories:
            del self.repositories[name]
            return self._save()
        return False
    
    def list(self) -> List[Repository]:
        """list all repositories"""
        return list(self.repositories.values())
    
    def get(self, name: str) -> Optional[Repository]:
        """get a repository by name"""
        return self.repositories.get(name)

