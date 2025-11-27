#include "../src/core/dependency.hpp"
#include <iostream>
#include <cassert>

using namespace std;

void test_dependency_parsing() {
    cout << "Testing dependency parsing..." << endl;
    
    // Simple dependency with constraint
    Dependency d1("numpy", ">=1.0.0");
    assert(d1.getName() == "numpy");
    assert(d1.getConstraints().size() == 1);
    
    // Dependency with multiple constraints
    Dependency d2("pandas", ">=1.0.0,<2.0.0");
    assert(d2.getName() == "pandas");
    assert(d2.getConstraints().size() == 2);
    
    // Dependency without constraints
    Dependency d3("requests", "");
    assert(d3.getName() == "requests");
    assert(d3.getConstraints().empty());
    
    cout << "  ✓ Dependency parsing tests passed" << endl;
}

void test_dependency_satisfaction() {
    cout << "Testing dependency satisfaction..." << endl;
    
    Dependency d1("numpy", ">=1.0.0,<2.0.0");
    
    assert(d1.satisfies(Version("1.5.0")));
    assert(d1.satisfies(Version("1.0.0")));
    assert(!d1.satisfies(Version("2.0.0")));
    assert(!d1.satisfies(Version("0.9.0")));
    
    // No constraints = any version
    Dependency d2("requests", "");
    assert(d2.satisfies(Version("1.0.0")));
    assert(d2.satisfies(Version("99.99.99")));
    
    cout << "  ✓ Dependency satisfaction tests passed" << endl;
}

void test_dependency_parse_string() {
    cout << "Testing dependency string parsing..." << endl;
    
    auto d1 = Dependency::parse("numpy >=1.0.0");
    assert(d1.getName() == "numpy");
    
    auto d2 = Dependency::parse("requests");
    assert(d2.getName() == "requests");
    assert(d2.getConstraints().empty());
    
    cout << "  ✓ Dependency string parsing tests passed" << endl;
}

int main() {
    cout << "\n=== Dependency Tests ===" << endl;
    
    try {
        test_dependency_parsing();
        test_dependency_satisfaction();
        test_dependency_parse_string();
        
        cout << "\n✓ All dependency tests passed!\n" << endl;
        return 0;
    } catch (const exception& e) {
        cerr << "\n✗ Test failed: " << e.what() << endl;
        return 1;
    }
}
