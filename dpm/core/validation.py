"""
validation.py - input sanitization and validation
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """raised when validation fails"""
    pass


def sanitize_package_name(name: str) -> str:
    """sanitize package name for safe use in URLs and commands
    
    removes dangerous characters and validates length
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Package name must be a non-empty string")
    
    # remove dangerous characters (keep only alphanumeric, dots, dashes, underscores)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', name)
    
    # check length limits (PyPI allows up to 214 chars)
    if len(sanitized) > 214:
        raise ValidationError(f"Package name too long (max 214 chars): {name}")
    
    if not sanitized:
        raise ValidationError(f"Package name becomes empty after sanitization: {name}")
    
    # check for valid characters (must start with alphanumeric)
    if not re.match(r'^[a-zA-Z0-9]', sanitized):
        raise ValidationError(f"Package name must start with alphanumeric: {name}")
    
    if sanitized != name:
        logger.warning(f"Package name sanitized: '{name}' -> '{sanitized}'")
    
    return sanitized


def validate_version_string(version: str) -> bool:
    """validate version string format"""
    if not version or not isinstance(version, str):
        return False
    
    # normalize whitespace
    version = version.strip()
    
    # check length
    if len(version) > 50:
        return False
    
    # check for basic semver pattern
    if not re.match(r'^[\d\.]+[\w\.\-\+]*$', version):
        return False
    
    return True


def sanitize_url(url: str) -> str:
    """sanitize URL to prevent injection attacks"""
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    
    # basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValidationError(f"URL must start with http:// or https://: {url}")
    
    # check for dangerous characters
    if any(char in url for char in ['\n', '\r', '\t', '\0']):
        raise ValidationError(f"URL contains invalid characters: {url}")
    
    return url


def validate_package_name(name: str) -> bool:
    """validate package name format"""
    try:
        sanitize_package_name(name)
        return True
    except ValidationError:
        return False


validation.py - input sanitization and validation
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """raised when validation fails"""
    pass


def sanitize_package_name(name: str) -> str:
    """sanitize package name for safe use in URLs and commands
    
    removes dangerous characters and validates length
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Package name must be a non-empty string")
    
    # remove dangerous characters (keep only alphanumeric, dots, dashes, underscores)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', name)
    
    # check length limits (PyPI allows up to 214 chars)
    if len(sanitized) > 214:
        raise ValidationError(f"Package name too long (max 214 chars): {name}")
    
    if not sanitized:
        raise ValidationError(f"Package name becomes empty after sanitization: {name}")
    
    # check for valid characters (must start with alphanumeric)
    if not re.match(r'^[a-zA-Z0-9]', sanitized):
        raise ValidationError(f"Package name must start with alphanumeric: {name}")
    
    if sanitized != name:
        logger.warning(f"Package name sanitized: '{name}' -> '{sanitized}'")
    
    return sanitized


def validate_version_string(version: str) -> bool:
    """validate version string format"""
    if not version or not isinstance(version, str):
        return False
    
    # normalize whitespace
    version = version.strip()
    
    # check length
    if len(version) > 50:
        return False
    
    # check for basic semver pattern
    if not re.match(r'^[\d\.]+[\w\.\-\+]*$', version):
        return False
    
    return True


def sanitize_url(url: str) -> str:
    """sanitize URL to prevent injection attacks"""
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    
    # basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValidationError(f"URL must start with http:// or https://: {url}")
    
    # check for dangerous characters
    if any(char in url for char in ['\n', '\r', '\t', '\0']):
        raise ValidationError(f"URL contains invalid characters: {url}")
    
    return url


def validate_package_name(name: str) -> bool:
    """validate package name format"""
    try:
        sanitize_package_name(name)
        return True
    except ValidationError:
        return False


validation.py - input sanitization and validation
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """raised when validation fails"""
    pass


def sanitize_package_name(name: str) -> str:
    """sanitize package name for safe use in URLs and commands
    
    removes dangerous characters and validates length
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Package name must be a non-empty string")
    
    # remove dangerous characters (keep only alphanumeric, dots, dashes, underscores)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', name)
    
    # check length limits (PyPI allows up to 214 chars)
    if len(sanitized) > 214:
        raise ValidationError(f"Package name too long (max 214 chars): {name}")
    
    if not sanitized:
        raise ValidationError(f"Package name becomes empty after sanitization: {name}")
    
    # check for valid characters (must start with alphanumeric)
    if not re.match(r'^[a-zA-Z0-9]', sanitized):
        raise ValidationError(f"Package name must start with alphanumeric: {name}")
    
    if sanitized != name:
        logger.warning(f"Package name sanitized: '{name}' -> '{sanitized}'")
    
    return sanitized


def validate_version_string(version: str) -> bool:
    """validate version string format"""
    if not version or not isinstance(version, str):
        return False
    
    # normalize whitespace
    version = version.strip()
    
    # check length
    if len(version) > 50:
        return False
    
    # check for basic semver pattern
    if not re.match(r'^[\d\.]+[\w\.\-\+]*$', version):
        return False
    
    return True


def sanitize_url(url: str) -> str:
    """sanitize URL to prevent injection attacks"""
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    
    # basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValidationError(f"URL must start with http:// or https://: {url}")
    
    # check for dangerous characters
    if any(char in url for char in ['\n', '\r', '\t', '\0']):
        raise ValidationError(f"URL contains invalid characters: {url}")
    
    return url


def validate_package_name(name: str) -> bool:
    """validate package name format"""
    try:
        sanitize_package_name(name)
        return True
    except ValidationError:
        return False


validation.py - input sanitization and validation
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """raised when validation fails"""
    pass


def sanitize_package_name(name: str) -> str:
    """sanitize package name for safe use in URLs and commands
    
    removes dangerous characters and validates length
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Package name must be a non-empty string")
    
    # remove dangerous characters (keep only alphanumeric, dots, dashes, underscores)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', name)
    
    # check length limits (PyPI allows up to 214 chars)
    if len(sanitized) > 214:
        raise ValidationError(f"Package name too long (max 214 chars): {name}")
    
    if not sanitized:
        raise ValidationError(f"Package name becomes empty after sanitization: {name}")
    
    # check for valid characters (must start with alphanumeric)
    if not re.match(r'^[a-zA-Z0-9]', sanitized):
        raise ValidationError(f"Package name must start with alphanumeric: {name}")
    
    if sanitized != name:
        logger.warning(f"Package name sanitized: '{name}' -> '{sanitized}'")
    
    return sanitized


def validate_version_string(version: str) -> bool:
    """validate version string format"""
    if not version or not isinstance(version, str):
        return False
    
    # normalize whitespace
    version = version.strip()
    
    # check length
    if len(version) > 50:
        return False
    
    # check for basic semver pattern
    if not re.match(r'^[\d\.]+[\w\.\-\+]*$', version):
        return False
    
    return True


def sanitize_url(url: str) -> str:
    """sanitize URL to prevent injection attacks"""
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    
    # basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValidationError(f"URL must start with http:// or https://: {url}")
    
    # check for dangerous characters
    if any(char in url for char in ['\n', '\r', '\t', '\0']):
        raise ValidationError(f"URL contains invalid characters: {url}")
    
    return url


def validate_package_name(name: str) -> bool:
    """validate package name format"""
    try:
        sanitize_package_name(name)
        return True
    except ValidationError:
        return False



