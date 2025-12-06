"""
manifest.py - for reading and writing dpm.json manifest files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Manifest:
    """for reading and writing dpm.json manifest files"""
    
    def __init__(self, manifest_path: str = "dpm.json"):
        self.manifest_path = Path(manifest_path)
    
    def exists(self) -> bool:
        """check if manifest file exists"""
        return self.manifest_path.exists()
    
    def read(self) -> Optional[Dict]:
        """read manifest file"""
        if not self.exists():
            return None
        
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def write(self, data: Dict) -> bool:
        """write manifest file"""
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def create_template(self, name: str = "my-project", version: str = "1.0.0") -> bool:
        """create a template manifest file"""
        template = {
            "name": name,
            "version": version,
            "description": "",
            "dependencies": {},
            "devDependencies": {},
            "sources": ["pypi", "npm"]
        }
        return self.write(template)
    
    def get_dependencies(self) -> Dict[str, str]:
        """get dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("dependencies", {})
    
    def get_dev_dependencies(self) -> Dict[str, str]:
        """get dev dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("devDependencies", {})
    
    def add_dependency(self, name: str, version: str, dev: bool = False) -> bool:
        """add a dependency to manifest"""
        data = self.read()
        if not data:
            data = {
                "name": "my-project",
                "version": "1.0.0",
                "dependencies": {},
                "devDependencies": {}
            }
        
        if dev:
            if "devDependencies" not in data:
                data["devDependencies"] = {}
            data["devDependencies"][name] = version
        else:
            if "dependencies" not in data:
                data["dependencies"] = {}
            data["dependencies"][name] = version
        
        return self.write(data)
    
    def remove_dependency(self, name: str) -> bool:
        """remove a dependency from manifest"""
        data = self.read()
        if not data:
            return False
        
        removed = False
        if "dependencies" in data and name in data["dependencies"]:
            del data["dependencies"][name]
            removed = True
        
        if "devDependencies" in data and name in data["devDependencies"]:
            del data["devDependencies"][name]
            removed = True
        
        if removed:
            return self.write(data)
        return False
    
    def get_sources(self) -> List[str]:
        """get configured sources"""
        data = self.read()
        if not data:
            return ["pypi", "npm"]
        return data.get("sources", ["pypi", "npm"])


manifest.py - for reading and writing dpm.json manifest files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Manifest:
    """for reading and writing dpm.json manifest files"""
    
    def __init__(self, manifest_path: str = "dpm.json"):
        self.manifest_path = Path(manifest_path)
    
    def exists(self) -> bool:
        """check if manifest file exists"""
        return self.manifest_path.exists()
    
    def read(self) -> Optional[Dict]:
        """read manifest file"""
        if not self.exists():
            return None
        
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def write(self, data: Dict) -> bool:
        """write manifest file"""
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def create_template(self, name: str = "my-project", version: str = "1.0.0") -> bool:
        """create a template manifest file"""
        template = {
            "name": name,
            "version": version,
            "description": "",
            "dependencies": {},
            "devDependencies": {},
            "sources": ["pypi", "npm"]
        }
        return self.write(template)
    
    def get_dependencies(self) -> Dict[str, str]:
        """get dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("dependencies", {})
    
    def get_dev_dependencies(self) -> Dict[str, str]:
        """get dev dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("devDependencies", {})
    
    def add_dependency(self, name: str, version: str, dev: bool = False) -> bool:
        """add a dependency to manifest"""
        data = self.read()
        if not data:
            data = {
                "name": "my-project",
                "version": "1.0.0",
                "dependencies": {},
                "devDependencies": {}
            }
        
        if dev:
            if "devDependencies" not in data:
                data["devDependencies"] = {}
            data["devDependencies"][name] = version
        else:
            if "dependencies" not in data:
                data["dependencies"] = {}
            data["dependencies"][name] = version
        
        return self.write(data)
    
    def remove_dependency(self, name: str) -> bool:
        """remove a dependency from manifest"""
        data = self.read()
        if not data:
            return False
        
        removed = False
        if "dependencies" in data and name in data["dependencies"]:
            del data["dependencies"][name]
            removed = True
        
        if "devDependencies" in data and name in data["devDependencies"]:
            del data["devDependencies"][name]
            removed = True
        
        if removed:
            return self.write(data)
        return False
    
    def get_sources(self) -> List[str]:
        """get configured sources"""
        data = self.read()
        if not data:
            return ["pypi", "npm"]
        return data.get("sources", ["pypi", "npm"])


manifest.py - for reading and writing dpm.json manifest files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Manifest:
    """for reading and writing dpm.json manifest files"""
    
    def __init__(self, manifest_path: str = "dpm.json"):
        self.manifest_path = Path(manifest_path)
    
    def exists(self) -> bool:
        """check if manifest file exists"""
        return self.manifest_path.exists()
    
    def read(self) -> Optional[Dict]:
        """read manifest file"""
        if not self.exists():
            return None
        
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def write(self, data: Dict) -> bool:
        """write manifest file"""
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def create_template(self, name: str = "my-project", version: str = "1.0.0") -> bool:
        """create a template manifest file"""
        template = {
            "name": name,
            "version": version,
            "description": "",
            "dependencies": {},
            "devDependencies": {},
            "sources": ["pypi", "npm"]
        }
        return self.write(template)
    
    def get_dependencies(self) -> Dict[str, str]:
        """get dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("dependencies", {})
    
    def get_dev_dependencies(self) -> Dict[str, str]:
        """get dev dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("devDependencies", {})
    
    def add_dependency(self, name: str, version: str, dev: bool = False) -> bool:
        """add a dependency to manifest"""
        data = self.read()
        if not data:
            data = {
                "name": "my-project",
                "version": "1.0.0",
                "dependencies": {},
                "devDependencies": {}
            }
        
        if dev:
            if "devDependencies" not in data:
                data["devDependencies"] = {}
            data["devDependencies"][name] = version
        else:
            if "dependencies" not in data:
                data["dependencies"] = {}
            data["dependencies"][name] = version
        
        return self.write(data)
    
    def remove_dependency(self, name: str) -> bool:
        """remove a dependency from manifest"""
        data = self.read()
        if not data:
            return False
        
        removed = False
        if "dependencies" in data and name in data["dependencies"]:
            del data["dependencies"][name]
            removed = True
        
        if "devDependencies" in data and name in data["devDependencies"]:
            del data["devDependencies"][name]
            removed = True
        
        if removed:
            return self.write(data)
        return False
    
    def get_sources(self) -> List[str]:
        """get configured sources"""
        data = self.read()
        if not data:
            return ["pypi", "npm"]
        return data.get("sources", ["pypi", "npm"])


manifest.py - for reading and writing dpm.json manifest files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Manifest:
    """for reading and writing dpm.json manifest files"""
    
    def __init__(self, manifest_path: str = "dpm.json"):
        self.manifest_path = Path(manifest_path)
    
    def exists(self) -> bool:
        """check if manifest file exists"""
        return self.manifest_path.exists()
    
    def read(self) -> Optional[Dict]:
        """read manifest file"""
        if not self.exists():
            return None
        
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def write(self, data: Dict) -> bool:
        """write manifest file"""
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def create_template(self, name: str = "my-project", version: str = "1.0.0") -> bool:
        """create a template manifest file"""
        template = {
            "name": name,
            "version": version,
            "description": "",
            "dependencies": {},
            "devDependencies": {},
            "sources": ["pypi", "npm"]
        }
        return self.write(template)
    
    def get_dependencies(self) -> Dict[str, str]:
        """get dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("dependencies", {})
    
    def get_dev_dependencies(self) -> Dict[str, str]:
        """get dev dependencies from manifest"""
        data = self.read()
        if not data:
            return {}
        return data.get("devDependencies", {})
    
    def add_dependency(self, name: str, version: str, dev: bool = False) -> bool:
        """add a dependency to manifest"""
        data = self.read()
        if not data:
            data = {
                "name": "my-project",
                "version": "1.0.0",
                "dependencies": {},
                "devDependencies": {}
            }
        
        if dev:
            if "devDependencies" not in data:
                data["devDependencies"] = {}
            data["devDependencies"][name] = version
        else:
            if "dependencies" not in data:
                data["dependencies"] = {}
            data["dependencies"][name] = version
        
        return self.write(data)
    
    def remove_dependency(self, name: str) -> bool:
        """remove a dependency from manifest"""
        data = self.read()
        if not data:
            return False
        
        removed = False
        if "dependencies" in data and name in data["dependencies"]:
            del data["dependencies"][name]
            removed = True
        
        if "devDependencies" in data and name in data["devDependencies"]:
            del data["devDependencies"][name]
            removed = True
        
        if removed:
            return self.write(data)
        return False
    
    def get_sources(self) -> List[str]:
        """get configured sources"""
        data = self.read()
        if not data:
            return ["pypi", "npm"]
        return data.get("sources", ["pypi", "npm"])


