"""
integrity.py - sha256 checksum verification for packages
"""

import hashlib
import base64
from typing import Optional


class Integrity:
    """for checking if a package file is corrupted or tampered with"""
    
    @staticmethod
    def calculate_sha256(data: bytes) -> str:
        """calculate sha256 hash of data"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def calculate_sha256_file(filepath: str) -> Optional[str]:
        """calculate sha256 hash of a file"""
        try:
            with open(filepath, 'rb') as f:
                return Integrity.calculate_sha256(f.read())
        except Exception:
            return None
    
    @staticmethod
    def to_base64(input_str: str) -> str:
        """encode to base64"""
        return base64.b64encode(input_str.encode()).decode()
    
    @staticmethod
    def from_base64(input_str: str) -> str:
        """decode from base64"""
        return base64.b64decode(input_str).decode()
    
    @staticmethod
    def verify(data: bytes, integrity_string: str) -> bool:
        """check if hash matches"""
        calculated = Integrity.calculate_sha256(data)
        # integrity_string can be in format "sha256:hexhash" or just hexhash
        if integrity_string.startswith("sha256:"):
            expected = integrity_string[7:]
        else:
            expected = integrity_string
        
        return calculated.lower() == expected.lower()
    
    @staticmethod
    def verify_file(filepath: str, integrity_string: str) -> bool:
        """verify file integrity"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            return Integrity.verify(data, integrity_string)
        except Exception:
            return False
    
    @staticmethod
    def format_integrity(hash_value: str) -> str:
        """format hash as integrity string"""
        return f"sha256:{hash_value}"


