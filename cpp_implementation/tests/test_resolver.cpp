#include "../src/resolver/resolver.hpp"
#include "../src/resolver/greedy.hpp"
#include "../src/resolver/backtrack.hpp"
#include "../src/sources/local.hpp"
#include "../src/json.hpp"
#include <iostream>
#include <fstream>
#include <cassert>
#include <filesystem>

using namespace std;
using json = nlohmann::json;
namespace fs = filesystem;

// Create test package files
void setup_test_packages(const string& test_dir) {
    fs::create_directories(test_dir);
    
    // Package A depends on B and C
    json pkg_a;
    pkg_a["name"] = "package-a";
    pkg_a["version"] = "1.0.0";
    pkg_a["dependencies"] = {{"package-b", ">=1.0.0"}, {"package-c", ">=1.0.0"}};
    
    ofstream(test_dir + "/package-a.json") << pkg_a.dump(2);
    
    // Package B depends on D
    json pkg_b;
    pkg_b["name"] = "package-b";
    pkg_b["version"] = "1.0.0";
    pkg_b["dependencies"] = {{"package-d", ">=1.0.0"}};
    
    ofstream(test_dir + "/package-b.json") << pkg_b.dump(2);
    
    // Package C (no dependencies)
    json pkg_c;
    pkg_c["name"] = "package-c";
    pkg_c["version"] = "1.0.0";
    pkg_c["dependencies"] = json::object();
    
    ofstream(test_dir + "/package-c.json") << pkg_c.dump(2);
    
    // Package D (no dependencies)
    json pkg_d;
    pkg_d["name"] = "package-d";
    pkg_d["version"] = "1.0.0";
    pkg_d["dependencies"] = json::object();
    
    ofstream(test_dir + "/package-d.json") << pkg_d.dump(2);
}

void cleanup_test_packages(const string& test_dir) {
    fs::remove_all(test_dir);
}

void test_greedy_resolver() {
    cout << "Testing greedy resolver..." << endl;
    
    string test_dir = "/tmp/dpm_test_packages";
    setup_test_packages(test_dir);
    
    auto local_source = make_shared<LocalSource>(test_dir);
    vector<shared_ptr<Source>> sources = {local_source};
    
    GreedyResolver resolver;
    auto result = resolver.resolve({"package-a"}, sources);
    
    assert(result.success);
    assert(result.selected_versions.size() == 4);
    assert(result.selected_versions.count("package-a") == 1);
    assert(result.selected_versions.count("package-b") == 1);
    assert(result.selected_versions.count("package-c") == 1);
    assert(result.selected_versions.count("package-d") == 1);
    
    cleanup_test_packages(test_dir);
    
    cout << "  ✓ Greedy resolver tests passed" << endl;
}

void test_nonexistent_package() {
    cout << "Testing non-existent package handling..." << endl;
    
    string test_dir = "/tmp/dpm_test_packages_empty";
    fs::create_directories(test_dir);
    
    auto local_source = make_shared<LocalSource>(test_dir);
    vector<shared_ptr<Source>> sources = {local_source};
    
    GreedyResolver resolver;
    auto result = resolver.resolve({"nonexistent-package"}, sources);
    
    assert(!result.success);
    assert(result.conflict_package == "nonexistent-package");
    assert(result.conflict_reason.find("not found") != string::npos);
    
    fs::remove_all(test_dir);
    
    cout << "  ✓ Non-existent package handling tests passed" << endl;
}

void test_hybrid_resolver() {
    cout << "Testing hybrid resolver..." << endl;
    
    string test_dir = "/tmp/dpm_test_packages_hybrid";
    setup_test_packages(test_dir);
    
    auto local_source = make_shared<LocalSource>(test_dir);
    vector<shared_ptr<Source>> sources = {local_source};
    
    DependencyResolver resolver;
    auto result = resolver.resolve({"package-a"}, sources);
    
    assert(result.success);
    assert(result.selected_versions.size() == 4);
    
    cleanup_test_packages(test_dir);
    
    cout << "  ✓ Hybrid resolver tests passed" << endl;
}

int main() {
    cout << "\n=== Resolver Tests ===" << endl;
    
    try {
        test_greedy_resolver();
        test_nonexistent_package();
        test_hybrid_resolver();
        
        cout << "\n✓ All resolver tests passed!\n" << endl;
        return 0;
    } catch (const exception& e) {
        cerr << "\n✗ Test failed: " << e.what() << endl;
        return 1;
    }
}



