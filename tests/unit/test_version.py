"""
test_version.py - unit tests for version parsing and comparison
"""

import sys
from pathlib import Path

# add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.version import Version, VersionConstraint, ConstraintOp


def test_version_parsing():
    """test version parsing"""
    # test semver
    v1 = Version("1.2.3")
    assert v1.major == 1
    assert v1.minor == 2
    assert v1.patch == 3
    assert v1.prerelease == ""
    
    # test with prerelease
    v2 = Version("2.0.0-alpha")
    assert v2.major == 2
    assert v2.minor == 0
    assert v2.patch == 0
    assert v2.prerelease == "alpha"
    
    # test two-part version
    v3 = Version("14.0")
    assert v3.major == 14
    assert v3.minor == 0
    assert v3.patch == 0
    
    print("[OK] Version parsing tests passed")


def test_version_comparison():
    """test version comparison"""
    v1 = Version("1.2.3")
    v2 = Version("1.2.4")
    v3 = Version("2.0.0")
    
    assert v1 < v2
    assert v2 < v3
    assert v1 < v3
    assert v2 > v1
    assert v3 > v1
    
    # test equality
    v4 = Version("1.2.3")
    assert v1 == v4
    
    # test stable vs prerelease
    v5 = Version("1.2.3-alpha")
    assert v1 > v5  # stable > prerelease
    
    print("[OK] Version comparison tests passed")


def test_version_constraints():
    """test version constraints"""
    # test >= constraint
    constraint = VersionConstraint(ConstraintOp.GE, Version("1.0.0"))
    assert constraint.satisfies(Version("1.0.0"))
    assert constraint.satisfies(Version("2.0.0"))
    assert not constraint.satisfies(Version("0.9.0"))
    
    # test == constraint
    constraint_eq = VersionConstraint(ConstraintOp.EQ, Version("1.2.3"))
    assert constraint_eq.satisfies(Version("1.2.3"))
    assert not constraint_eq.satisfies(Version("1.2.4"))
    
    # test tilde
    constraint_tilde = VersionConstraint(ConstraintOp.TILDE, Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.9"))
    assert not constraint_tilde.satisfies(Version("1.3.0"))
    
    # test caret
    constraint_caret = VersionConstraint(ConstraintOp.CARET, Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.9.9"))
    assert not constraint_caret.satisfies(Version("2.0.0"))
    
    print("[OK] Version constraint tests passed")


def test_constraint_parsing():
    """test constraint parsing"""
    # parse >= constraint
    c1 = VersionConstraint.parse(">=1.0.0")
    assert c1 is not None
    assert c1.op == ConstraintOp.GE
    assert c1.version == Version("1.0.0")
    
    # parse multiple constraints
    constraints = VersionConstraint.parse_multiple(">=1.0.0,<2.0.0")
    assert len(constraints) == 2
    assert constraints[0].op == ConstraintOp.GE
    assert constraints[1].op == ConstraintOp.LT
    
    print("[OK] Constraint parsing tests passed")


if __name__ == "__main__":
    test_version_parsing()
    test_version_comparison()
    test_version_constraints()
    test_constraint_parsing()
    print("\n[OK] All version tests passed!")


test_version.py - unit tests for version parsing and comparison
"""

import sys
from pathlib import Path

# add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.version import Version, VersionConstraint, ConstraintOp


def test_version_parsing():
    """test version parsing"""
    # test semver
    v1 = Version("1.2.3")
    assert v1.major == 1
    assert v1.minor == 2
    assert v1.patch == 3
    assert v1.prerelease == ""
    
    # test with prerelease
    v2 = Version("2.0.0-alpha")
    assert v2.major == 2
    assert v2.minor == 0
    assert v2.patch == 0
    assert v2.prerelease == "alpha"
    
    # test two-part version
    v3 = Version("14.0")
    assert v3.major == 14
    assert v3.minor == 0
    assert v3.patch == 0
    
    print("[OK] Version parsing tests passed")


def test_version_comparison():
    """test version comparison"""
    v1 = Version("1.2.3")
    v2 = Version("1.2.4")
    v3 = Version("2.0.0")
    
    assert v1 < v2
    assert v2 < v3
    assert v1 < v3
    assert v2 > v1
    assert v3 > v1
    
    # test equality
    v4 = Version("1.2.3")
    assert v1 == v4
    
    # test stable vs prerelease
    v5 = Version("1.2.3-alpha")
    assert v1 > v5  # stable > prerelease
    
    print("[OK] Version comparison tests passed")


def test_version_constraints():
    """test version constraints"""
    # test >= constraint
    constraint = VersionConstraint(ConstraintOp.GE, Version("1.0.0"))
    assert constraint.satisfies(Version("1.0.0"))
    assert constraint.satisfies(Version("2.0.0"))
    assert not constraint.satisfies(Version("0.9.0"))
    
    # test == constraint
    constraint_eq = VersionConstraint(ConstraintOp.EQ, Version("1.2.3"))
    assert constraint_eq.satisfies(Version("1.2.3"))
    assert not constraint_eq.satisfies(Version("1.2.4"))
    
    # test tilde
    constraint_tilde = VersionConstraint(ConstraintOp.TILDE, Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.9"))
    assert not constraint_tilde.satisfies(Version("1.3.0"))
    
    # test caret
    constraint_caret = VersionConstraint(ConstraintOp.CARET, Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.9.9"))
    assert not constraint_caret.satisfies(Version("2.0.0"))
    
    print("[OK] Version constraint tests passed")


def test_constraint_parsing():
    """test constraint parsing"""
    # parse >= constraint
    c1 = VersionConstraint.parse(">=1.0.0")
    assert c1 is not None
    assert c1.op == ConstraintOp.GE
    assert c1.version == Version("1.0.0")
    
    # parse multiple constraints
    constraints = VersionConstraint.parse_multiple(">=1.0.0,<2.0.0")
    assert len(constraints) == 2
    assert constraints[0].op == ConstraintOp.GE
    assert constraints[1].op == ConstraintOp.LT
    
    print("[OK] Constraint parsing tests passed")


if __name__ == "__main__":
    test_version_parsing()
    test_version_comparison()
    test_version_constraints()
    test_constraint_parsing()
    print("\n[OK] All version tests passed!")


test_version.py - unit tests for version parsing and comparison
"""

import sys
from pathlib import Path

# add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.version import Version, VersionConstraint, ConstraintOp


def test_version_parsing():
    """test version parsing"""
    # test semver
    v1 = Version("1.2.3")
    assert v1.major == 1
    assert v1.minor == 2
    assert v1.patch == 3
    assert v1.prerelease == ""
    
    # test with prerelease
    v2 = Version("2.0.0-alpha")
    assert v2.major == 2
    assert v2.minor == 0
    assert v2.patch == 0
    assert v2.prerelease == "alpha"
    
    # test two-part version
    v3 = Version("14.0")
    assert v3.major == 14
    assert v3.minor == 0
    assert v3.patch == 0
    
    print("[OK] Version parsing tests passed")


def test_version_comparison():
    """test version comparison"""
    v1 = Version("1.2.3")
    v2 = Version("1.2.4")
    v3 = Version("2.0.0")
    
    assert v1 < v2
    assert v2 < v3
    assert v1 < v3
    assert v2 > v1
    assert v3 > v1
    
    # test equality
    v4 = Version("1.2.3")
    assert v1 == v4
    
    # test stable vs prerelease
    v5 = Version("1.2.3-alpha")
    assert v1 > v5  # stable > prerelease
    
    print("[OK] Version comparison tests passed")


def test_version_constraints():
    """test version constraints"""
    # test >= constraint
    constraint = VersionConstraint(ConstraintOp.GE, Version("1.0.0"))
    assert constraint.satisfies(Version("1.0.0"))
    assert constraint.satisfies(Version("2.0.0"))
    assert not constraint.satisfies(Version("0.9.0"))
    
    # test == constraint
    constraint_eq = VersionConstraint(ConstraintOp.EQ, Version("1.2.3"))
    assert constraint_eq.satisfies(Version("1.2.3"))
    assert not constraint_eq.satisfies(Version("1.2.4"))
    
    # test tilde
    constraint_tilde = VersionConstraint(ConstraintOp.TILDE, Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.9"))
    assert not constraint_tilde.satisfies(Version("1.3.0"))
    
    # test caret
    constraint_caret = VersionConstraint(ConstraintOp.CARET, Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.9.9"))
    assert not constraint_caret.satisfies(Version("2.0.0"))
    
    print("[OK] Version constraint tests passed")


def test_constraint_parsing():
    """test constraint parsing"""
    # parse >= constraint
    c1 = VersionConstraint.parse(">=1.0.0")
    assert c1 is not None
    assert c1.op == ConstraintOp.GE
    assert c1.version == Version("1.0.0")
    
    # parse multiple constraints
    constraints = VersionConstraint.parse_multiple(">=1.0.0,<2.0.0")
    assert len(constraints) == 2
    assert constraints[0].op == ConstraintOp.GE
    assert constraints[1].op == ConstraintOp.LT
    
    print("[OK] Constraint parsing tests passed")


if __name__ == "__main__":
    test_version_parsing()
    test_version_comparison()
    test_version_constraints()
    test_constraint_parsing()
    print("\n[OK] All version tests passed!")


test_version.py - unit tests for version parsing and comparison
"""

import sys
from pathlib import Path

# add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.version import Version, VersionConstraint, ConstraintOp


def test_version_parsing():
    """test version parsing"""
    # test semver
    v1 = Version("1.2.3")
    assert v1.major == 1
    assert v1.minor == 2
    assert v1.patch == 3
    assert v1.prerelease == ""
    
    # test with prerelease
    v2 = Version("2.0.0-alpha")
    assert v2.major == 2
    assert v2.minor == 0
    assert v2.patch == 0
    assert v2.prerelease == "alpha"
    
    # test two-part version
    v3 = Version("14.0")
    assert v3.major == 14
    assert v3.minor == 0
    assert v3.patch == 0
    
    print("[OK] Version parsing tests passed")


def test_version_comparison():
    """test version comparison"""
    v1 = Version("1.2.3")
    v2 = Version("1.2.4")
    v3 = Version("2.0.0")
    
    assert v1 < v2
    assert v2 < v3
    assert v1 < v3
    assert v2 > v1
    assert v3 > v1
    
    # test equality
    v4 = Version("1.2.3")
    assert v1 == v4
    
    # test stable vs prerelease
    v5 = Version("1.2.3-alpha")
    assert v1 > v5  # stable > prerelease
    
    print("[OK] Version comparison tests passed")


def test_version_constraints():
    """test version constraints"""
    # test >= constraint
    constraint = VersionConstraint(ConstraintOp.GE, Version("1.0.0"))
    assert constraint.satisfies(Version("1.0.0"))
    assert constraint.satisfies(Version("2.0.0"))
    assert not constraint.satisfies(Version("0.9.0"))
    
    # test == constraint
    constraint_eq = VersionConstraint(ConstraintOp.EQ, Version("1.2.3"))
    assert constraint_eq.satisfies(Version("1.2.3"))
    assert not constraint_eq.satisfies(Version("1.2.4"))
    
    # test tilde
    constraint_tilde = VersionConstraint(ConstraintOp.TILDE, Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.3"))
    assert constraint_tilde.satisfies(Version("1.2.9"))
    assert not constraint_tilde.satisfies(Version("1.3.0"))
    
    # test caret
    constraint_caret = VersionConstraint(ConstraintOp.CARET, Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.2.3"))
    assert constraint_caret.satisfies(Version("1.9.9"))
    assert not constraint_caret.satisfies(Version("2.0.0"))
    
    print("[OK] Version constraint tests passed")


def test_constraint_parsing():
    """test constraint parsing"""
    # parse >= constraint
    c1 = VersionConstraint.parse(">=1.0.0")
    assert c1 is not None
    assert c1.op == ConstraintOp.GE
    assert c1.version == Version("1.0.0")
    
    # parse multiple constraints
    constraints = VersionConstraint.parse_multiple(">=1.0.0,<2.0.0")
    assert len(constraints) == 2
    assert constraints[0].op == ConstraintOp.GE
    assert constraints[1].op == ConstraintOp.LT
    
    print("[OK] Constraint parsing tests passed")


if __name__ == "__main__":
    test_version_parsing()
    test_version_comparison()
    test_version_constraints()
    test_constraint_parsing()
    print("\n[OK] All version tests passed!")




