#include "../src/core/version.hpp"
#include <iostream>
#include <cassert>

using namespace std;

void test_version_parsing() {
    cout << "Testing version parsing..." << endl;
    
    Version v1("1.2.3");
    assert(v1.getMajor() == 1);
    assert(v1.getMinor() == 2);
    assert(v1.getPatch() == 3);
    assert(v1.isStable());
    
    Version v2("2.0.0-alpha");
    assert(v2.getMajor() == 2);
    assert(v2.getMinor() == 0);
    assert(v2.getPatch() == 0);
    assert(!v2.isStable());
    assert(v2.getPrerelease() == "alpha");
    
    Version v3("1.0.0+build123");
    assert(v3.getBuild() == "build123");
    
    cout << "  ✓ Version parsing tests passed" << endl;
}

void test_version_comparison() {
    cout << "Testing version comparison..." << endl;
    
    Version v1("1.0.0");
    Version v2("1.0.1");
    Version v3("1.1.0");
    Version v4("2.0.0");
    Version v5("1.0.0-alpha");
    Version v6("1.0.0-beta");
    
    // Basic comparisons
    assert(v1 < v2);
    assert(v2 < v3);
    assert(v3 < v4);
    assert(v1 <= v1);
    assert(v1 == v1);
    assert(v1 != v2);
    
    // Prerelease comparisons
    assert(v5 < v1);  // alpha < stable
    assert(v5 < v6);  // alpha < beta
    
    cout << "  ✓ Version comparison tests passed" << endl;
}

void test_version_constraints() {
    cout << "Testing version constraints..." << endl;
    
    Version v1("1.2.3");
    Version v2("2.0.0");
    Version v3("1.2.0");
    
    // Test >=
    auto c1 = VersionConstraint::parse(">=1.2.0");
    assert(c1.has_value());
    assert(c1->satisfies(v1));
    assert(c1->satisfies(v2));
    assert(c1->satisfies(v3));
    
    // Test <
    auto c2 = VersionConstraint::parse("<2.0.0");
    assert(c2.has_value());
    assert(c2->satisfies(v1));
    assert(!c2->satisfies(v2));
    
    // Test ==
    auto c3 = VersionConstraint::parse("==1.2.3");
    assert(c3.has_value());
    assert(c3->satisfies(v1));
    assert(!c3->satisfies(v2));
    
    // Test !=
    auto c4 = VersionConstraint::parse("!=1.2.3");
    assert(c4.has_value());
    assert(!c4->satisfies(v1));
    assert(c4->satisfies(v2));
    
    cout << "  ✓ Version constraint tests passed" << endl;
}

void test_tilde_constraints() {
    cout << "Testing tilde constraints..." << endl;
    
    // ~1.2.3 means >=1.2.3 and <1.3.0
    auto c = VersionConstraint::parse("~1.2.3");
    assert(c.has_value());
    
    assert(c->satisfies(Version("1.2.3")));
    assert(c->satisfies(Version("1.2.9")));
    assert(!c->satisfies(Version("1.3.0")));
    assert(!c->satisfies(Version("1.2.2")));
    assert(!c->satisfies(Version("2.0.0")));
    
    cout << "  ✓ Tilde constraint tests passed" << endl;
}

void test_caret_constraints() {
    cout << "Testing caret constraints..." << endl;
    
    // ^1.2.3 means >=1.2.3 and <2.0.0
    auto c1 = VersionConstraint::parse("^1.2.3");
    assert(c1.has_value());
    
    assert(c1->satisfies(Version("1.2.3")));
    assert(c1->satisfies(Version("1.9.9")));
    assert(!c1->satisfies(Version("2.0.0")));
    assert(!c1->satisfies(Version("1.2.2")));
    
    // ^0.2.3 means >=0.2.3 and <0.3.0
    auto c2 = VersionConstraint::parse("^0.2.3");
    assert(c2.has_value());
    
    assert(c2->satisfies(Version("0.2.3")));
    assert(c2->satisfies(Version("0.2.9")));
    assert(!c2->satisfies(Version("0.3.0")));
    
    cout << "  ✓ Caret constraint tests passed" << endl;
}

void test_multiple_constraints() {
    cout << "Testing multiple constraints..." << endl;
    
    auto constraints = VersionConstraint::parseMultiple(">=1.0.0,<2.0.0");
    assert(constraints.size() == 2);
    
    Version v1("1.5.0");
    Version v2("2.5.0");
    Version v3("0.5.0");
    
    bool v1_satisfies = true;
    bool v2_satisfies = true;
    bool v3_satisfies = true;
    
    for (const auto& c : constraints) {
        if (!c.satisfies(v1)) v1_satisfies = false;
        if (!c.satisfies(v2)) v2_satisfies = false;
        if (!c.satisfies(v3)) v3_satisfies = false;
    }
    
    assert(v1_satisfies);
    assert(!v2_satisfies);
    assert(!v3_satisfies);
    
    cout << "  ✓ Multiple constraint tests passed" << endl;
}

int main() {
    cout << "\n=== Version Tests ===" << endl;
    
    try {
        test_version_parsing();
        test_version_comparison();
        test_version_constraints();
        test_tilde_constraints();
        test_caret_constraints();
        test_multiple_constraints();
        
        cout << "\n✓ All version tests passed!\n" << endl;
        return 0;
    } catch (const exception& e) {
        cerr << "\n✗ Test failed: " << e.what() << endl;
        return 1;
    }
}
