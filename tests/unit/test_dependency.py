"""
test_dependency.py - unit tests for dependency parsing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.dependency import Dependency
from dpm.core.version import Version


def test_dependency_parsing():
    """test dependency parsing"""
    # parse simple dependency
    dep1 = Dependency.parse("numpy")
    assert dep1.name == "numpy"
    assert len(dep1.constraints) == 0
    
    # parse with constraint
    dep2 = Dependency.parse("numpy>=1.0.0")
    assert dep2.name == "numpy"
    assert len(dep2.constraints) == 1
    assert dep2.constraints[0].satisfies(Version("1.0.0"))
    assert dep2.constraints[0].satisfies(Version("2.0.0"))
    assert not dep2.constraints[0].satisfies(Version("0.9.0"))
    
    # parse with multiple constraints
    dep3 = Dependency.parse("flask>=1.0.0,<2.0.0")
    assert dep3.name == "flask"
    assert len(dep3.constraints) == 2
    
    print("[OK] Dependency parsing tests passed")


def test_dependency_satisfies():
    """test dependency satisfaction"""
    dep = Dependency.parse("numpy>=1.0.0,<2.0.0")
    
    assert dep.satisfies(Version("1.0.0"))
    assert dep.satisfies(Version("1.5.0"))
    assert dep.satisfies(Version("1.9.9"))
    assert not dep.satisfies(Version("0.9.0"))
    assert not dep.satisfies(Version("2.0.0"))
    
    print("[OK] Dependency satisfaction tests passed")


if __name__ == "__main__":
    test_dependency_parsing()
    test_dependency_satisfies()
    print("\n[OK] All dependency tests passed!")


test_dependency.py - unit tests for dependency parsing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.dependency import Dependency
from dpm.core.version import Version


def test_dependency_parsing():
    """test dependency parsing"""
    # parse simple dependency
    dep1 = Dependency.parse("numpy")
    assert dep1.name == "numpy"
    assert len(dep1.constraints) == 0
    
    # parse with constraint
    dep2 = Dependency.parse("numpy>=1.0.0")
    assert dep2.name == "numpy"
    assert len(dep2.constraints) == 1
    assert dep2.constraints[0].satisfies(Version("1.0.0"))
    assert dep2.constraints[0].satisfies(Version("2.0.0"))
    assert not dep2.constraints[0].satisfies(Version("0.9.0"))
    
    # parse with multiple constraints
    dep3 = Dependency.parse("flask>=1.0.0,<2.0.0")
    assert dep3.name == "flask"
    assert len(dep3.constraints) == 2
    
    print("[OK] Dependency parsing tests passed")


def test_dependency_satisfies():
    """test dependency satisfaction"""
    dep = Dependency.parse("numpy>=1.0.0,<2.0.0")
    
    assert dep.satisfies(Version("1.0.0"))
    assert dep.satisfies(Version("1.5.0"))
    assert dep.satisfies(Version("1.9.9"))
    assert not dep.satisfies(Version("0.9.0"))
    assert not dep.satisfies(Version("2.0.0"))
    
    print("[OK] Dependency satisfaction tests passed")


if __name__ == "__main__":
    test_dependency_parsing()
    test_dependency_satisfies()
    print("\n[OK] All dependency tests passed!")


test_dependency.py - unit tests for dependency parsing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.dependency import Dependency
from dpm.core.version import Version


def test_dependency_parsing():
    """test dependency parsing"""
    # parse simple dependency
    dep1 = Dependency.parse("numpy")
    assert dep1.name == "numpy"
    assert len(dep1.constraints) == 0
    
    # parse with constraint
    dep2 = Dependency.parse("numpy>=1.0.0")
    assert dep2.name == "numpy"
    assert len(dep2.constraints) == 1
    assert dep2.constraints[0].satisfies(Version("1.0.0"))
    assert dep2.constraints[0].satisfies(Version("2.0.0"))
    assert not dep2.constraints[0].satisfies(Version("0.9.0"))
    
    # parse with multiple constraints
    dep3 = Dependency.parse("flask>=1.0.0,<2.0.0")
    assert dep3.name == "flask"
    assert len(dep3.constraints) == 2
    
    print("[OK] Dependency parsing tests passed")


def test_dependency_satisfies():
    """test dependency satisfaction"""
    dep = Dependency.parse("numpy>=1.0.0,<2.0.0")
    
    assert dep.satisfies(Version("1.0.0"))
    assert dep.satisfies(Version("1.5.0"))
    assert dep.satisfies(Version("1.9.9"))
    assert not dep.satisfies(Version("0.9.0"))
    assert not dep.satisfies(Version("2.0.0"))
    
    print("[OK] Dependency satisfaction tests passed")


if __name__ == "__main__":
    test_dependency_parsing()
    test_dependency_satisfies()
    print("\n[OK] All dependency tests passed!")


test_dependency.py - unit tests for dependency parsing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.core.dependency import Dependency
from dpm.core.version import Version


def test_dependency_parsing():
    """test dependency parsing"""
    # parse simple dependency
    dep1 = Dependency.parse("numpy")
    assert dep1.name == "numpy"
    assert len(dep1.constraints) == 0
    
    # parse with constraint
    dep2 = Dependency.parse("numpy>=1.0.0")
    assert dep2.name == "numpy"
    assert len(dep2.constraints) == 1
    assert dep2.constraints[0].satisfies(Version("1.0.0"))
    assert dep2.constraints[0].satisfies(Version("2.0.0"))
    assert not dep2.constraints[0].satisfies(Version("0.9.0"))
    
    # parse with multiple constraints
    dep3 = Dependency.parse("flask>=1.0.0,<2.0.0")
    assert dep3.name == "flask"
    assert len(dep3.constraints) == 2
    
    print("[OK] Dependency parsing tests passed")


def test_dependency_satisfies():
    """test dependency satisfaction"""
    dep = Dependency.parse("numpy>=1.0.0,<2.0.0")
    
    assert dep.satisfies(Version("1.0.0"))
    assert dep.satisfies(Version("1.5.0"))
    assert dep.satisfies(Version("1.9.9"))
    assert not dep.satisfies(Version("0.9.0"))
    assert not dep.satisfies(Version("2.0.0"))
    
    print("[OK] Dependency satisfaction tests passed")


if __name__ == "__main__":
    test_dependency_parsing()
    test_dependency_satisfies()
    print("\n[OK] All dependency tests passed!")




