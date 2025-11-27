#include "../src/resolver/graph.hpp"
#include "../src/core/package.hpp"
#include <iostream>
#include <cassert>
#include <algorithm>

using namespace std;

void test_graph_basic() {
    cout << "Testing basic graph operations..." << endl;
    
    DependencyGraph graph;
    
    Package p1("numpy", "1.0.0", "python");
    Package p2("scipy", "1.0.0", "python");
    Package p3("pandas", "1.0.0", "python");
    
    graph.addPackage(p1);
    graph.addPackage(p2);
    graph.addPackage(p3);
    
    assert(graph.size() == 3);
    assert(graph.hasPackage("numpy"));
    assert(graph.hasPackage("scipy"));
    assert(!graph.hasPackage("nonexistent"));
    
    cout << "  ✓ Basic graph operations tests passed" << endl;
}

void test_graph_dependencies() {
    cout << "Testing graph dependencies..." << endl;
    
    DependencyGraph graph;
    
    Package p1("app", "1.0.0", "python");
    Package p2("numpy", "1.0.0", "python");
    Package p3("scipy", "1.0.0", "python");
    
    graph.addPackage(p1);
    graph.addPackage(p2);
    graph.addPackage(p3);
    
    // app depends on numpy and scipy
    graph.addDependency("app", "numpy");
    graph.addDependency("app", "scipy");
    // scipy depends on numpy
    graph.addDependency("scipy", "numpy");
    
    auto app_deps = graph.getDependencies("app");
    assert(app_deps.size() == 2);
    
    auto numpy_dependents = graph.getDependents("numpy");
    assert(numpy_dependents.size() == 2);
    
    cout << "  ✓ Graph dependencies tests passed" << endl;
}

void test_topological_sort() {
    cout << "Testing topological sort..." << endl;
    
    DependencyGraph graph;
    
    Package p1("app", "1.0.0", "python");
    Package p2("numpy", "1.0.0", "python");
    Package p3("scipy", "1.0.0", "python");
    
    graph.addPackage(p1);
    graph.addPackage(p2);
    graph.addPackage(p3);
    
    graph.addDependency("app", "scipy");
    graph.addDependency("scipy", "numpy");
    
    auto order = graph.topologicalSort();
    
    // Verify all packages are present
    assert(order.size() == 3);
    assert(find(order.begin(), order.end(), "app") != order.end());
    assert(find(order.begin(), order.end(), "scipy") != order.end());
    assert(find(order.begin(), order.end(), "numpy") != order.end());
    
    cout << "  ✓ Topological sort tests passed" << endl;
}

void test_cycle_detection() {
    cout << "Testing cycle detection..." << endl;
    
    DependencyGraph graph;
    
    Package p1("a", "1.0.0", "python");
    Package p2("b", "1.0.0", "python");
    Package p3("c", "1.0.0", "python");
    
    graph.addPackage(p1);
    graph.addPackage(p2);
    graph.addPackage(p3);
    
    // No cycle
    graph.addDependency("a", "b");
    graph.addDependency("b", "c");
    assert(!graph.hasCycle());
    
    // Add cycle: c -> a
    graph.addDependency("c", "a");
    assert(graph.hasCycle());
    
    auto cycle = graph.getCycle();
    assert(!cycle.empty());
    
    cout << "  ✓ Cycle detection tests passed" << endl;
}

void test_scc() {
    cout << "Testing strongly connected components..." << endl;
    
    DependencyGraph graph;
    
    Package p1("a", "1.0.0", "python");
    Package p2("b", "1.0.0", "python");
    Package p3("c", "1.0.0", "python");
    Package p4("d", "1.0.0", "python");
    
    graph.addPackage(p1);
    graph.addPackage(p2);
    graph.addPackage(p3);
    graph.addPackage(p4);
    
    // Create cycle: a -> b -> c -> a
    graph.addDependency("a", "b");
    graph.addDependency("b", "c");
    graph.addDependency("c", "a");
    // d is separate
    graph.addDependency("a", "d");
    
    auto sccs = graph.getStronglyConnectedComponents();
    
    // Should have at least 2 SCCs: {a,b,c} and {d}
    assert(sccs.size() >= 2);
    
    cout << "  ✓ SCC tests passed" << endl;
}

int main() {
    cout << "\n=== Graph Tests ===" << endl;
    
    try {
        test_graph_basic();
        test_graph_dependencies();
        test_topological_sort();
        test_cycle_detection();
        test_scc();
        
        cout << "\n✓ All graph tests passed!\n" << endl;
        return 0;
    } catch (const exception& e) {
        cerr << "\n✗ Test failed: " << e.what() << endl;
        return 1;
    }
}
