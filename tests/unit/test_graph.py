"""
test_graph.py - unit tests for dependency graph
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.resolver.graph import DependencyGraph
from dpm.core.package import Package


def test_graph_operations():
    """test basic graph operations"""
    graph = DependencyGraph()
    
    # add packages
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    
    # add dependency
    graph.add_dependency("A", "B")
    
    assert "A" in graph.get_packages()
    assert "B" in graph.get_packages()
    assert "B" in graph.get_dependencies("A")
    assert "A" in graph.get_dependents("B")
    
    print("[OK] Graph operations tests passed")


def test_cycle_detection():
    """test cycle detection"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # create cycle: A -> B -> C -> A
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    graph.add_dependency("C", "A")
    
    assert graph.has_cycle()
    cycle = graph.get_cycle()
    assert len(cycle) > 0
    
    print("[OK] Cycle detection tests passed")


def test_topological_sort():
    """test topological sort"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # A depends on B, B depends on C
    # so installation order should be: C, B, A (dependencies first)
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    
    order = graph.topological_sort()
    # verify all packages are in the result
    assert len(order) == 3
    assert "A" in order
    assert "B" in order
    assert "C" in order
    
    # C should come before B, B before A (dependencies before dependents)
    assert order.index("C") < order.index("B")
    assert order.index("B") < order.index("A")
    
    print("[OK] Topological sort tests passed")


if __name__ == "__main__":
    test_graph_operations()
    test_cycle_detection()
    test_topological_sort()
    print("\n[OK] All graph tests passed!")


"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.resolver.graph import DependencyGraph
from dpm.core.package import Package


def test_graph_operations():
    """test basic graph operations"""
    graph = DependencyGraph()
    
    # add packages
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    
    # add dependency
    graph.add_dependency("A", "B")
    
    assert "A" in graph.get_packages()
    assert "B" in graph.get_packages()
    assert "B" in graph.get_dependencies("A")
    assert "A" in graph.get_dependents("B")
    
    print("[OK] Graph operations tests passed")


def test_cycle_detection():
    """test cycle detection"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # create cycle: A -> B -> C -> A
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    graph.add_dependency("C", "A")
    
    assert graph.has_cycle()
    cycle = graph.get_cycle()
    assert len(cycle) > 0
    
    print("[OK] Cycle detection tests passed")


def test_topological_sort():
    """test topological sort"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # A depends on B, B depends on C
    # so installation order should be: C, B, A (dependencies first)
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    
    order = graph.topological_sort()
    # verify all packages are in the result
    assert len(order) == 3
    assert "A" in order
    assert "B" in order
    assert "C" in order
    
    # C should come before B, B before A (dependencies before dependents)
    assert order.index("C") < order.index("B")
    assert order.index("B") < order.index("A")
    
    print("[OK] Topological sort tests passed")


if __name__ == "__main__":
    test_graph_operations()
    test_cycle_detection()
    test_topological_sort()
    print("\n[OK] All graph tests passed!")


"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.resolver.graph import DependencyGraph
from dpm.core.package import Package


def test_graph_operations():
    """test basic graph operations"""
    graph = DependencyGraph()
    
    # add packages
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    
    # add dependency
    graph.add_dependency("A", "B")
    
    assert "A" in graph.get_packages()
    assert "B" in graph.get_packages()
    assert "B" in graph.get_dependencies("A")
    assert "A" in graph.get_dependents("B")
    
    print("[OK] Graph operations tests passed")


def test_cycle_detection():
    """test cycle detection"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # create cycle: A -> B -> C -> A
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    graph.add_dependency("C", "A")
    
    assert graph.has_cycle()
    cycle = graph.get_cycle()
    assert len(cycle) > 0
    
    print("[OK] Cycle detection tests passed")


def test_topological_sort():
    """test topological sort"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # A depends on B, B depends on C
    # so installation order should be: C, B, A (dependencies first)
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    
    order = graph.topological_sort()
    # verify all packages are in the result
    assert len(order) == 3
    assert "A" in order
    assert "B" in order
    assert "C" in order
    
    # C should come before B, B before A (dependencies before dependents)
    assert order.index("C") < order.index("B")
    assert order.index("B") < order.index("A")
    
    print("[OK] Topological sort tests passed")


if __name__ == "__main__":
    test_graph_operations()
    test_cycle_detection()
    test_topological_sort()
    print("\n[OK] All graph tests passed!")


"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dpm.resolver.graph import DependencyGraph
from dpm.core.package import Package


def test_graph_operations():
    """test basic graph operations"""
    graph = DependencyGraph()
    
    # add packages
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    
    # add dependency
    graph.add_dependency("A", "B")
    
    assert "A" in graph.get_packages()
    assert "B" in graph.get_packages()
    assert "B" in graph.get_dependencies("A")
    assert "A" in graph.get_dependents("B")
    
    print("[OK] Graph operations tests passed")


def test_cycle_detection():
    """test cycle detection"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # create cycle: A -> B -> C -> A
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    graph.add_dependency("C", "A")
    
    assert graph.has_cycle()
    cycle = graph.get_cycle()
    assert len(cycle) > 0
    
    print("[OK] Cycle detection tests passed")


def test_topological_sort():
    """test topological sort"""
    graph = DependencyGraph()
    
    pkg1 = Package("A", "1.0.0", "python")
    pkg2 = Package("B", "1.0.0", "python")
    pkg3 = Package("C", "1.0.0", "python")
    
    graph.add_package(pkg1)
    graph.add_package(pkg2)
    graph.add_package(pkg3)
    
    # A depends on B, B depends on C
    # so installation order should be: C, B, A (dependencies first)
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    
    order = graph.topological_sort()
    # verify all packages are in the result
    assert len(order) == 3
    assert "A" in order
    assert "B" in order
    assert "C" in order
    
    # C should come before B, B before A (dependencies before dependents)
    assert order.index("C") < order.index("B")
    assert order.index("B") < order.index("A")
    
    print("[OK] Topological sort tests passed")


if __name__ == "__main__":
    test_graph_operations()
    test_cycle_detection()
    test_topological_sort()
    print("\n[OK] All graph tests passed!")

