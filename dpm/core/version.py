"""
version.py - semantic versioning and constraints
"""

import re
from typing import Optional, List
from enum import Enum


class ConstraintOp(Enum):
    """different ways to constrain a version"""
    EQ = "=="      # exact match
    NE = "!="      # not this version
    LT = "<"       # less than
    LE = "<="      # less than or equal
    GT = ">"       # greater than
    GE = ">="      # greater than or equal
    TILDE = "~"    # allows patch updates (1.2.x)
    CARET = "^"    # allows minor updates (1.x.x)


class Version:
    """represents a semantic version like 1.2.3-beta+build"""
    
    def __init__(self, version_str: Optional[str] = None):
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.prerelease = ""  # stuff after the dash like "alpha" or "rc1"
        self.build = ""       # stuff after the plus sign
        
        if version_str:
            if not self.parse(version_str):
                raise ValueError(f"Invalid version string: {version_str}")
    
    @staticmethod
    def is_valid_version_string(version_str: str) -> bool:
        """validate version string format before parsing"""
        if not version_str or not isinstance(version_str, str):
            return False
        
        # normalize whitespace
        version_str = version_str.strip()
        
        # check length (reasonable limit)
        if len(version_str) > 50:
            return False
        
        # check for basic semver pattern
        # allow digits, dots, dashes, plus signs, and alphanumeric for prerelease/build
        if not re.match(r'^[\d\.]+[\w\.\-\+]*$', version_str):
            return False
        
        return True
    
    def parse(self, version_str: str) -> bool:
        """tries to parse something like "1.2.3" or "2.0.0-alpha" """
        # validate input first
        if not Version.is_valid_version_string(version_str):
            return False
        
        # normalize whitespace
        version_str = version_str.strip()
        
        # try full semver first: major.minor.patch[-prerelease][+build]
        semver_regex = r"^(\d+)\.(\d+)\.(\d+)(?:-([\w\.-]+))?(?:\+([\w\.-]+))?$"
        match = re.match(semver_regex, version_str)
        
        if match:
            try:
                self.major = int(match.group(1))
                self.minor = int(match.group(2))
                self.patch = int(match.group(3))
                self.prerelease = match.group(4) or ""
                self.build = match.group(5) or ""
                return True
            except (ValueError, IndexError):
                return False
        
        # try major.minor format (e.g., "14.0", "15.3")
        two_part_regex = r"^(\d+)\.(\d+)(?:-([\w\.-]+))?(?:\+([\w\.-]+))?$"
        match = re.match(two_part_regex, version_str)
        if match:
            try:
                self.major = int(match.group(1))
                self.minor = int(match.group(2))
                self.patch = 0
                self.prerelease = match.group(3) or ""
                self.build = match.group(4) or ""
                return True
            except (ValueError, IndexError):
                return False
        
        # try single number (e.g., "2024")
        single_regex = r"^(\d+)(?:-([\w\.-]+))?(?:\+([\w\.-]+))?$"
        match = re.match(single_regex, version_str)
        if match:
            try:
                self.major = int(match.group(1))
                self.minor = 0
                self.patch = 0
                self.prerelease = match.group(2) or ""
                self.build = match.group(3) or ""
                return True
            except (ValueError, IndexError):
                return False
        
        return False
    
    def __lt__(self, other: 'Version') -> bool:
        """comparison stuff - needed for sorting versions"""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        
        # compare prerelease: stable > prerelease, then lexicographic
        if not self.prerelease and other.prerelease:
            return False
        if self.prerelease and not other.prerelease:
            return True
        if self.prerelease and other.prerelease:
            return self._compare_prerelease(self.prerelease, other.prerelease) < 0
        
        return False
    
    def __le__(self, other: 'Version') -> bool:
        return self < other or self == other
    
    def __gt__(self, other: 'Version') -> bool:
        return other < self
    
    def __ge__(self, other: 'Version') -> bool:
        return self > other or self == other
    
    def __eq__(self, other: 'Version') -> bool:
        return (self.major == other.major and
                self.minor == other.minor and
                self.patch == other.patch and
                self.prerelease == other.prerelease)
    
    def __ne__(self, other: 'Version') -> bool:
        return not (self == other)
    
    def __str__(self) -> str:
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            result += f"-{self.prerelease}"
        if self.build:
            result += f"+{self.build}"
        return result
    
    def __repr__(self) -> str:
        return f"Version('{self}')"
    
    def is_stable(self) -> bool:
        """stable means no prerelease tag like -alpha or -beta"""
        return not self.prerelease
    
    def _compare_prerelease(self, a: str, b: str) -> int:
        """compares prerelease strings alphabetically mostly"""
        if a < b:
            return -1
        if a > b:
            return 1
        return 0


class VersionConstraint:
    """like ">=1.0.0" or "^2.3.4" """
    
    def __init__(self, op: ConstraintOp = ConstraintOp.EQ, version: Optional[Version] = None):
        self.op = op
        self.version = version or Version()
    
    @staticmethod
    def parse(constraint_str: str) -> Optional['VersionConstraint']:
        """parses stuff like ">=1.0.0" or "~2.1.0" """
        trimmed = constraint_str.strip()
        if not trimmed:
            return None
        
        op = ConstraintOp.EQ
        version_str = trimmed
        
        # parse operator
        if trimmed.startswith(">="):
            op = ConstraintOp.GE
            version_str = trimmed[2:].strip()
        elif trimmed.startswith("<="):
            op = ConstraintOp.LE
            version_str = trimmed[2:].strip()
        elif trimmed.startswith("!="):
            op = ConstraintOp.NE
            version_str = trimmed[2:].strip()
        elif trimmed.startswith("=="):
            op = ConstraintOp.EQ
            version_str = trimmed[2:].strip()
        elif trimmed.startswith(">"):
            op = ConstraintOp.GT
            version_str = trimmed[1:].strip()
        elif trimmed.startswith("<"):
            op = ConstraintOp.LT
            version_str = trimmed[1:].strip()
        elif trimmed.startswith("~"):
            op = ConstraintOp.TILDE
            version_str = trimmed[1:].strip()
        elif trimmed.startswith("^"):
            op = ConstraintOp.CARET
            version_str = trimmed[1:].strip()
        
        try:
            version = Version(version_str)
            return VersionConstraint(op, version)
        except ValueError:
            return None
    
    @staticmethod
    def parse_multiple(constraints_str: str) -> List['VersionConstraint']:
        """handles comma separated constraints like ">=1.0.0,<2.0.0" """
        constraints = []
        for constraint_str in constraints_str.split(','):
            parsed = VersionConstraint.parse(constraint_str.strip())
            if parsed:
                constraints.append(parsed)
        return constraints
    
    def satisfies(self, version: Version) -> bool:
        """checks if a version matches this constraint"""
        if self.op == ConstraintOp.EQ:
            return version == self.version
        elif self.op == ConstraintOp.NE:
            return version != self.version
        elif self.op == ConstraintOp.LT:
            return version < self.version
        elif self.op == ConstraintOp.LE:
            return version <= self.version
        elif self.op == ConstraintOp.GT:
            return version > self.version
        elif self.op == ConstraintOp.GE:
            return version >= self.version
        elif self.op == ConstraintOp.TILDE:
            return self._satisfies_tilde(version)
        elif self.op == ConstraintOp.CARET:
            return self._satisfies_caret(version)
        return False
    
    def _satisfies_tilde(self, v: Version) -> bool:
        """tilde: ~1.2.3 means >=1.2.3 and <1.3.0"""
        if v.major != self.version.major:
            return False
        if v.minor < self.version.minor:
            return False
        if v.minor > self.version.minor:
            return False  # must be < 1.3.0
        # same minor version, check patch
        return v >= self.version
    
    def _satisfies_caret(self, v: Version) -> bool:
        """caret: ^1.2.3 means >=1.2.3 and <2.0.0"""
        if not (v >= self.version):
            return False
        
        if self.version.major == 0:
            if self.version.minor == 0:
                # ^0.0.3 means >=0.0.3 and <0.0.4
                return v.major == 0 and v.minor == 0 and v.patch < self.version.patch + 1
            # ^0.2.3 means >=0.2.3 and <0.3.0
            return v.major == 0 and v.minor < self.version.minor + 1
        
        # ^1.2.3 means >=1.2.3 and <2.0.0
        return v.major < self.version.major + 1
    
    def __str__(self) -> str:
        op_str = {
            ConstraintOp.EQ: "==",
            ConstraintOp.NE: "!=",
            ConstraintOp.LT: "<",
            ConstraintOp.LE: "<=",
            ConstraintOp.GT: ">",
            ConstraintOp.GE: ">=",
            ConstraintOp.TILDE: "~",
            ConstraintOp.CARET: "^"
        }.get(self.op, "==")
        return f"{op_str}{self.version}"

