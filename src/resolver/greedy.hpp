#pragma once

#include "../core/package.hpp"
#include "../core/version.hpp"
#include "../core/dependency.hpp"
#include "../resolver/graph.hpp"
#include "../sources/source.hpp"
#include <string>
#include <map>
#include <vector>
#include <memory>
#include <optional>

using namespace std;

// result from greedy resolution attempt
struct GreedyResult {
    bool success;
    map<string, string> selected_versions;  // what versions we picked
    string conflict_package;  // which package caused issues
    string conflict_reason;
    vector<string> not_found_packages;  // packages we couldn't find anywhere
};

// greedy resolver - fast but might not find solution if there are conflicts
// basically just picks the latest version that works and hopes for the best
class GreedyResolver {
public:
    GreedyResolver();
    
    // try to resolve using greedy approach
    GreedyResult resolve(const vector<string>& requested_packages,
                        const vector<shared_ptr<Source>>& sources);
    
    map<string, string> getSelectedVersions() const { return selected_versions; }
    
private:
    map<string, string> selected_versions;
    
    // builds the dependency graph and tracks which packages we couldn't find
    pair<DependencyGraph, vector<string>> buildGraphWithErrors(
        const vector<string>& requested_packages,
        const vector<shared_ptr<Source>>& sources);
    
    // picks the best version based on our heuristics
    // prefers: latest stable > latest prerelease > already selected
    optional<string> selectBestVersion(const string& package,
                                      const vector<string>& available_versions,
                                      const vector<VersionConstraint>& constraints,
                                      const vector<shared_ptr<Source>>& sources);
    
    // gets all the constraints on a package from things that depend on it
    vector<VersionConstraint> getConstraints(const string& package,
                                             const DependencyGraph& graph);
    
    // scores a version - higher is better
    int scoreVersion(const Version& version,
                    const vector<VersionConstraint>& constraints,
                    const map<string, string>& selected);
};
