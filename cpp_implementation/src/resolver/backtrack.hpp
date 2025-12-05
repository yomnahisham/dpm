#pragma once

#include "../core/package.hpp"
#include "../core/version.hpp"
#include "../core/dependency.hpp"
#include "../resolver/graph.hpp"
#include "../sources/source.hpp"
#include <string>
#include <map>
#include <vector>
#include <set>
#include <memory>
#include <unordered_set>
#include <optional>

using namespace std;

// result from backtracking
struct BacktrackResult {
    bool success;
    map<string, string> selected_versions;
    string failure_reason;
};

// represents current state during backtracking
struct ResolutionState {
    map<string, string> selected_versions;  // what we've picked so far
    set<string> unassigned_packages;        // what we still need to pick
    int depth;                               // how deep we are in the search
    
    string hash() const;  // for memoization
    bool operator==(const ResolutionState& other) const;
};

// backtracking resolver - slower but guaranteed to find solution if one exists
// uses constraint satisfaction techniques like forward checking and mrv
class BacktrackResolver {
public:
    BacktrackResolver();
    
    // resolve using backtracking - can take initial selections from greedy
    BacktrackResult resolve(const vector<string>& requested_packages,
                           const map<string, string>& initial_selections,
                           const vector<shared_ptr<Source>>& sources);
    
    // limit search depth to avoid infinite loops (0 = no limit)
    void setMaxDepth(int depth) { max_depth = depth; }
    
private:
    int max_depth;
    unordered_set<string> failed_states;  // memoization - don't try states we know fail
    
    // builds graph with all packages and their constraints
    DependencyGraph buildConstraintGraph(const vector<string>& requested_packages,
                                        const vector<shared_ptr<Source>>& sources);
    
    // the actual recursive backtracking
    bool backtrack(ResolutionState& state,
                   const DependencyGraph& graph,
                   const vector<shared_ptr<Source>>& sources);
    
    // mrv heuristic - pick the package with fewest valid versions left
    // this helps us fail faster if there's no solution
    optional<string> selectUnassignedPackage_MRV(const ResolutionState& state,
                                                 const DependencyGraph& graph,
                                                 const vector<shared_ptr<Source>>& sources);
    
    // orders versions to try - latest first usually
    vector<string> getOrderedVersions(const string& package,
                                     const vector<shared_ptr<Source>>& sources,
                                     const ResolutionState& state);
    
    // forward checking - checks if picking this version would make it
    // impossible to satisfy some other package's constraints
    bool forwardCheck(const string& package,
                     const string& version,
                     const ResolutionState& state,
                     const DependencyGraph& graph,
                     const vector<shared_ptr<Source>>& sources);
    
    // updates constraints after we pick a version
    void propagateConstraints(const string& package,
                             const string& version,
                             ResolutionState& state,
                             const DependencyGraph& graph);
    
    // are we done?
    bool isComplete(const ResolutionState& state) const;
    
    // is the current state broken?
    bool hasConflict(const ResolutionState& state, const DependencyGraph& graph) const;
};

