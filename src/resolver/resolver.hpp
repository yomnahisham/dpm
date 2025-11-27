#pragma once

#include "greedy.hpp"
#include "backtrack.hpp"
#include "../core/package.hpp"
#include "../sources/source.hpp"
#include <string>
#include <vector>
#include <map>
#include <memory>

using namespace std;

// what we return after trying to resolve dependencies
struct ResolutionResult {
    bool success;
    map<string, string> selected_versions;  // package name -> version string
    string error_message;
    bool used_backtracking;  // true if we had to fall back to backtracking
};

// main resolver class - tries greedy first, then backtracking if needed
class DependencyResolver {
public:
    DependencyResolver();
    
    // the main function - give it packages, get back resolved versions
    ResolutionResult resolve(const vector<string>& requested_packages,
                            const vector<shared_ptr<Source>>& sources);
    
    // mostly for testing - forces backtracking even when greedy works
    void setAlwaysBacktrack(bool always) { always_backtrack = always; }
    
private:
    bool always_backtrack;
    GreedyResolver greedy_resolver;
    BacktrackResolver backtrack_resolver;
    
    // figures out which packages are causing problems
    vector<string> identifyConflictRegion(const GreedyResult& greedy_result,
                                         const vector<string>& requested_packages);
};

