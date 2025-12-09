"""
errors.py - better error messages and error context
"""

from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """structured error information"""
    message: str
    error_type: str  # conflict, not_found, network, etc
    suggestions: List[str] = None
    conflicting_packages: List[str] = None
    dependency_chain: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.conflicting_packages is None:
            self.conflicting_packages = []
        if self.dependency_chain is None:
            self.dependency_chain = []
    
    def format(self) -> str:
        """format error message with context"""
        lines = [f"Error: {self.message}"]
        
        if self.error_type == "conflict":
            if self.conflicting_packages:
                lines.append(f"\nConflicting packages: {', '.join(self.conflicting_packages)}")
            if self.dependency_chain:
                lines.append(f"Dependency chain: {' -> '.join(self.dependency_chain)}")
        
        if self.suggestions:
            lines.append("\nSuggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  - {suggestion}")
        
        return "\n".join(lines)


class DPMError(Exception):
    """base exception for DPM errors"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        self.message = message
        self.context = context
        super().__init__(message)
    
    def __str__(self):
        if self.context:
            return self.context.format()
        return self.message


class PackageNotFoundError(DPMError):
    """package not found in any source"""
    def __init__(self, package_name: str, sources: List[str]):
        context = ErrorContext(
            message=f"Package '{package_name}' not found in any source",
            error_type="not_found",
            suggestions=[
                f"Check if the package name is correct",
                f"Try searching: dpm search {package_name}",
                f"Available sources: {', '.join(sources)}"
            ]
        )
        super().__init__(context.message, context)


class DependencyConflictError(DPMError):
    """dependency version conflict"""
    def __init__(self, package: str, conflicts: Dict[str, List[str]], dependency_chain: List[str] = None):
        conflicting_packages = list(conflicts.keys())
        suggestions = [
            f"Try updating conflicting packages to compatible versions",
            f"Use 'dpm resolve {package}' to see detailed conflict information"
        ]
        
        context = ErrorContext(
            message=f"Version conflict for package '{package}'",
            error_type="conflict",
            suggestions=suggestions,
            conflicting_packages=conflicting_packages,
            dependency_chain=dependency_chain or []
        )
        super().__init__(context.message, context)


class NetworkError(DPMError):
    """network request failed"""
    def __init__(self, url: str, reason: str = ""):
        suggestions = [
            "Check your internet connection",
            "Try again later",
            "Use --offline flag to work with cached data"
        ]
        
        context = ErrorContext(
            message=f"Network error: Failed to fetch {url}",
            error_type="network",
            suggestions=suggestions
        )
        if reason:
            context.message += f" ({reason})"
        
        super().__init__(context.message, context)


class IntegrityError(DPMError):
    """package integrity verification failed"""
    def __init__(self, package: str, expected: str, actual: str):
        suggestions = [
            f"Package {package} may be corrupted or tampered with",
            "Try downloading again",
            "Use --skip-integrity to bypass verification (not recommended)"
        ]
        
        context = ErrorContext(
            message=f"Integrity check failed for {package}",
            error_type="integrity",
            suggestions=suggestions
        )
        
        super().__init__(context.message, context)


errors.py - better error messages and error context
"""

from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """structured error information"""
    message: str
    error_type: str  # conflict, not_found, network, etc
    suggestions: List[str] = None
    conflicting_packages: List[str] = None
    dependency_chain: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.conflicting_packages is None:
            self.conflicting_packages = []
        if self.dependency_chain is None:
            self.dependency_chain = []
    
    def format(self) -> str:
        """format error message with context"""
        lines = [f"Error: {self.message}"]
        
        if self.error_type == "conflict":
            if self.conflicting_packages:
                lines.append(f"\nConflicting packages: {', '.join(self.conflicting_packages)}")
            if self.dependency_chain:
                lines.append(f"Dependency chain: {' -> '.join(self.dependency_chain)}")
        
        if self.suggestions:
            lines.append("\nSuggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  - {suggestion}")
        
        return "\n".join(lines)


class DPMError(Exception):
    """base exception for DPM errors"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        self.message = message
        self.context = context
        super().__init__(message)
    
    def __str__(self):
        if self.context:
            return self.context.format()
        return self.message


class PackageNotFoundError(DPMError):
    """package not found in any source"""
    def __init__(self, package_name: str, sources: List[str]):
        context = ErrorContext(
            message=f"Package '{package_name}' not found in any source",
            error_type="not_found",
            suggestions=[
                f"Check if the package name is correct",
                f"Try searching: dpm search {package_name}",
                f"Available sources: {', '.join(sources)}"
            ]
        )
        super().__init__(context.message, context)


class DependencyConflictError(DPMError):
    """dependency version conflict"""
    def __init__(self, package: str, conflicts: Dict[str, List[str]], dependency_chain: List[str] = None):
        conflicting_packages = list(conflicts.keys())
        suggestions = [
            f"Try updating conflicting packages to compatible versions",
            f"Use 'dpm resolve {package}' to see detailed conflict information"
        ]
        
        context = ErrorContext(
            message=f"Version conflict for package '{package}'",
            error_type="conflict",
            suggestions=suggestions,
            conflicting_packages=conflicting_packages,
            dependency_chain=dependency_chain or []
        )
        super().__init__(context.message, context)


class NetworkError(DPMError):
    """network request failed"""
    def __init__(self, url: str, reason: str = ""):
        suggestions = [
            "Check your internet connection",
            "Try again later",
            "Use --offline flag to work with cached data"
        ]
        
        context = ErrorContext(
            message=f"Network error: Failed to fetch {url}",
            error_type="network",
            suggestions=suggestions
        )
        if reason:
            context.message += f" ({reason})"
        
        super().__init__(context.message, context)


class IntegrityError(DPMError):
    """package integrity verification failed"""
    def __init__(self, package: str, expected: str, actual: str):
        suggestions = [
            f"Package {package} may be corrupted or tampered with",
            "Try downloading again",
            "Use --skip-integrity to bypass verification (not recommended)"
        ]
        
        context = ErrorContext(
            message=f"Integrity check failed for {package}",
            error_type="integrity",
            suggestions=suggestions
        )
        
        super().__init__(context.message, context)


errors.py - better error messages and error context
"""

from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """structured error information"""
    message: str
    error_type: str  # conflict, not_found, network, etc
    suggestions: List[str] = None
    conflicting_packages: List[str] = None
    dependency_chain: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.conflicting_packages is None:
            self.conflicting_packages = []
        if self.dependency_chain is None:
            self.dependency_chain = []
    
    def format(self) -> str:
        """format error message with context"""
        lines = [f"Error: {self.message}"]
        
        if self.error_type == "conflict":
            if self.conflicting_packages:
                lines.append(f"\nConflicting packages: {', '.join(self.conflicting_packages)}")
            if self.dependency_chain:
                lines.append(f"Dependency chain: {' -> '.join(self.dependency_chain)}")
        
        if self.suggestions:
            lines.append("\nSuggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  - {suggestion}")
        
        return "\n".join(lines)


class DPMError(Exception):
    """base exception for DPM errors"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        self.message = message
        self.context = context
        super().__init__(message)
    
    def __str__(self):
        if self.context:
            return self.context.format()
        return self.message


class PackageNotFoundError(DPMError):
    """package not found in any source"""
    def __init__(self, package_name: str, sources: List[str]):
        context = ErrorContext(
            message=f"Package '{package_name}' not found in any source",
            error_type="not_found",
            suggestions=[
                f"Check if the package name is correct",
                f"Try searching: dpm search {package_name}",
                f"Available sources: {', '.join(sources)}"
            ]
        )
        super().__init__(context.message, context)


class DependencyConflictError(DPMError):
    """dependency version conflict"""
    def __init__(self, package: str, conflicts: Dict[str, List[str]], dependency_chain: List[str] = None):
        conflicting_packages = list(conflicts.keys())
        suggestions = [
            f"Try updating conflicting packages to compatible versions",
            f"Use 'dpm resolve {package}' to see detailed conflict information"
        ]
        
        context = ErrorContext(
            message=f"Version conflict for package '{package}'",
            error_type="conflict",
            suggestions=suggestions,
            conflicting_packages=conflicting_packages,
            dependency_chain=dependency_chain or []
        )
        super().__init__(context.message, context)


class NetworkError(DPMError):
    """network request failed"""
    def __init__(self, url: str, reason: str = ""):
        suggestions = [
            "Check your internet connection",
            "Try again later",
            "Use --offline flag to work with cached data"
        ]
        
        context = ErrorContext(
            message=f"Network error: Failed to fetch {url}",
            error_type="network",
            suggestions=suggestions
        )
        if reason:
            context.message += f" ({reason})"
        
        super().__init__(context.message, context)


class IntegrityError(DPMError):
    """package integrity verification failed"""
    def __init__(self, package: str, expected: str, actual: str):
        suggestions = [
            f"Package {package} may be corrupted or tampered with",
            "Try downloading again",
            "Use --skip-integrity to bypass verification (not recommended)"
        ]
        
        context = ErrorContext(
            message=f"Integrity check failed for {package}",
            error_type="integrity",
            suggestions=suggestions
        )
        
        super().__init__(context.message, context)


errors.py - better error messages and error context
"""

from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """structured error information"""
    message: str
    error_type: str  # conflict, not_found, network, etc
    suggestions: List[str] = None
    conflicting_packages: List[str] = None
    dependency_chain: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.conflicting_packages is None:
            self.conflicting_packages = []
        if self.dependency_chain is None:
            self.dependency_chain = []
    
    def format(self) -> str:
        """format error message with context"""
        lines = [f"Error: {self.message}"]
        
        if self.error_type == "conflict":
            if self.conflicting_packages:
                lines.append(f"\nConflicting packages: {', '.join(self.conflicting_packages)}")
            if self.dependency_chain:
                lines.append(f"Dependency chain: {' -> '.join(self.dependency_chain)}")
        
        if self.suggestions:
            lines.append("\nSuggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  - {suggestion}")
        
        return "\n".join(lines)


class DPMError(Exception):
    """base exception for DPM errors"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        self.message = message
        self.context = context
        super().__init__(message)
    
    def __str__(self):
        if self.context:
            return self.context.format()
        return self.message


class PackageNotFoundError(DPMError):
    """package not found in any source"""
    def __init__(self, package_name: str, sources: List[str]):
        context = ErrorContext(
            message=f"Package '{package_name}' not found in any source",
            error_type="not_found",
            suggestions=[
                f"Check if the package name is correct",
                f"Try searching: dpm search {package_name}",
                f"Available sources: {', '.join(sources)}"
            ]
        )
        super().__init__(context.message, context)


class DependencyConflictError(DPMError):
    """dependency version conflict"""
    def __init__(self, package: str, conflicts: Dict[str, List[str]], dependency_chain: List[str] = None):
        conflicting_packages = list(conflicts.keys())
        suggestions = [
            f"Try updating conflicting packages to compatible versions",
            f"Use 'dpm resolve {package}' to see detailed conflict information"
        ]
        
        context = ErrorContext(
            message=f"Version conflict for package '{package}'",
            error_type="conflict",
            suggestions=suggestions,
            conflicting_packages=conflicting_packages,
            dependency_chain=dependency_chain or []
        )
        super().__init__(context.message, context)


class NetworkError(DPMError):
    """network request failed"""
    def __init__(self, url: str, reason: str = ""):
        suggestions = [
            "Check your internet connection",
            "Try again later",
            "Use --offline flag to work with cached data"
        ]
        
        context = ErrorContext(
            message=f"Network error: Failed to fetch {url}",
            error_type="network",
            suggestions=suggestions
        )
        if reason:
            context.message += f" ({reason})"
        
        super().__init__(context.message, context)


class IntegrityError(DPMError):
    """package integrity verification failed"""
    def __init__(self, package: str, expected: str, actual: str):
        suggestions = [
            f"Package {package} may be corrupted or tampered with",
            "Try downloading again",
            "Use --skip-integrity to bypass verification (not recommended)"
        ]
        
        context = ErrorContext(
            message=f"Integrity check failed for {package}",
            error_type="integrity",
            suggestions=suggestions
        )
        
        super().__init__(context.message, context)




