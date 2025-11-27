#include "backtrack.hpp"
#include "../core/dependency.hpp"
#include "../core/version.hpp"
#include <algorithm>
#include <sstream>
#include <functional>
#include <climits>

using namespace std;

BacktrackResolver::BacktrackResolver() : max_depth(0) {}

string ResolutionState::hash() const {
    ostringstream oss;
    for (const auto& pair : selected_versions) {
        oss << pair.first << ":" << pair.second << ";";
    }
    return oss.str();
}

bool ResolutionState::operator==(const ResolutionState& other) const {
    return selected_versions == other.selected_versions;
}

DependencyGraph BacktrackResolver::buildConstraintGraph(const vector<string>& requested_packages, const vector<shared_ptr<Source>>& sources) {
    DependencyGraph graph;
    
    // similar to greedy, but build complete graph
    vector<string> queue = requested_packages;
    map<string, bool> processed;
    
    while (!queue.empty()) {
        string package_name = queue.back();
        queue.pop_back();
        
        if (processed[package_name]) {
            continue;
        }
        processed[package_name] = true;
        
        // Find source
        shared_ptr<Source> source = nullptr;
        for (const auto& s : sources) {
            if (s->packageExists(package_name)) {
                source = s;
                break;
            }
        }
        
        if (!source) {
            continue;
        }
        
        // Get all versions and process dependencies
        vector<string> versions = source->getAvailableVersions(package_name);
        if (versions.empty()) {
            continue;
        }
        
        // Use latest version to get dependency structure
        auto package_opt = source->fetchLatest(package_name);
        if (!package_opt.has_value()) {
            continue;
        }
        
        Package package = package_opt.value();
        graph.addPackage(package);
        
        // Add dependencies
        for (const auto& dep : package.getDependencies()) {
            string dep_name = dep.getName();
            graph.addDependency(package_name, dep_name);
            
            if (!processed[dep_name]) {
                queue.push_back(dep_name);
            }
        }
    }
    
    return graph;
}

optional<string> BacktrackResolver::selectUnassignedPackage_MRV(const ResolutionState& state,
                                                                const DependencyGraph& graph,
                                                                const vector<shared_ptr<Source>>& sources) {
    string best_package;
    int min_remaining = INT_MAX;
    
    for (const auto& package_name : state.unassigned_packages) {
        // Get available versions
        shared_ptr<Source> source = nullptr;
        for (const auto& s : sources) {
            if (s->packageExists(package_name)) {
                source = s;
                break;
            }
        }
        
        if (!source) {
            continue;
        }
        
        vector<string> versions = source->getAvailableVersions(package_name);
        
        // Count how many versions satisfy current constraints
        // (simplified - would need to check constraints)
        int remaining = versions.size();
        
        if (remaining < min_remaining && remaining > 0) {
            min_remaining = remaining;
            best_package = package_name;
        }
    }
    
    if (best_package.empty()) {
        return nullopt;
    }
    
    return best_package;
}

vector<string> BacktrackResolver::getOrderedVersions(const string& package,
                                                    const vector<shared_ptr<Source>>& sources,
                                                    const ResolutionState& state) {
    // Find source
    shared_ptr<Source> source = nullptr;
    for (const auto& s : sources) {
        if (s->packageExists(package)) {
            source = s;
            break;
        }
    }
    
    if (!source) {
        return vector<string>();
    }
    
    vector<string> versions = source->getAvailableVersions(package);
    
    // Sort: latest first, stable preferred
    vector<pair<Version, string>> version_objs;
    for (const auto& v_str : versions) {
        try {
            Version v(v_str);
            version_objs.push_back({v, v_str});
        } catch (...) {
            // Skip invalid
        }
    }
    
    sort(version_objs.begin(), version_objs.end(),
         [](const pair<Version, string>& a, const pair<Version, string>& b) {
             // Prefer stable
             if (a.first.isStable() != b.first.isStable()) {
                 return a.first.isStable() > b.first.isStable();
             }
             // Then prefer newer
             return a.first > b.first;
         });
    
    vector<string> result;
    for (const auto& pair : version_objs) {
        result.push_back(pair.second);
    }
    
    return result;
}

bool BacktrackResolver::forwardCheck(const string& package,
                                     const string& version,
                                     const ResolutionState& state,
                                     const DependencyGraph& graph,
                                     const vector<shared_ptr<Source>>& sources) {
    // Create temporary state with this assignment
    ResolutionState temp_state = state;
    temp_state.selected_versions[package] = version;
    temp_state.unassigned_packages.erase(package);
    
    // Check if any unassigned package becomes impossible
    for (const auto& unassigned : temp_state.unassigned_packages) {
        // Get available versions
        shared_ptr<Source> source = nullptr;
        for (const auto& s : sources) {
            if (s->packageExists(unassigned)) {
                source = s;
                break;
            }
        }
        
        if (!source) {
            continue;
        }
        
        vector<string> available = source->getAvailableVersions(unassigned);
        
        // Check if any version is still possible (simplified check)
        bool has_possible = false;
        for (const auto& v_str : available) {
            // Would need to check constraints here
            has_possible = true;
            break;
        }
        
        if (!has_possible) {
            return false; // Forward check failed
        }
    }
    
    return true;
}

void BacktrackResolver::propagateConstraints(const string& package,
                                            const string& version,
                                            ResolutionState& state,
                                            const DependencyGraph& graph) {
    // Constraints are implicitly handled through the graph structure
    // In a full implementation, we would update constraint sets here
}

bool BacktrackResolver::isComplete(const ResolutionState& state) const {
    return state.unassigned_packages.empty();
}

bool BacktrackResolver::hasConflict(const ResolutionState& state, const DependencyGraph& graph) const {
    // Check for cycle
    if (graph.hasCycle()) {
        return true;
    }
    
    // Check version constraints (simplified)
    // In full implementation, would check all constraints
    return false;
}

bool BacktrackResolver::backtrack(ResolutionState& state,
                                  const DependencyGraph& graph,
                                  const vector<shared_ptr<Source>>& sources) {
    // Check if complete
    if (isComplete(state)) {
        return !hasConflict(state, graph);
    }
    
    // Check depth limit
    if (max_depth > 0 && state.depth >= max_depth) {
        return false;
    }
    
    // Memoization check
    string state_hash = state.hash();
    if (failed_states.find(state_hash) != failed_states.end()) {
        return false;
    }
    
    // Select unassigned package (MRV heuristic)
    auto package_opt = selectUnassignedPackage_MRV(state, graph, sources);
    if (!package_opt.has_value()) {
        return false;
    }
    
    string package = package_opt.value();
    
    // Get ordered versions
    vector<string> versions = getOrderedVersions(package, sources, state);
    
    // Try each version
    for (const auto& version : versions) {
        // Forward checking
        if (!forwardCheck(package, version, state, graph, sources)) {
            continue;
        }
        
        // Make assignment
        ResolutionState new_state = state;
        new_state.selected_versions[package] = version;
        new_state.unassigned_packages.erase(package);
        new_state.depth = state.depth + 1;
        
        // Propagate constraints
        propagateConstraints(package, version, new_state, graph);
        
        // Recursive call
        if (backtrack(new_state, graph, sources)) {
            state = new_state;
            return true;
        }
    }
    
    // All versions failed - mark state as failed
    failed_states.insert(state_hash);
    return false;
}

BacktrackResult BacktrackResolver::resolve(const vector<string>& requested_packages,
                                          const map<string, string>& initial_selections,
                                          const vector<shared_ptr<Source>>& sources) {
    failed_states.clear();
    BacktrackResult result;
    result.success = false;
    
    // Build constraint graph
    DependencyGraph graph = buildConstraintGraph(requested_packages, sources);
    
    // Initialize state
    ResolutionState state;
    state.selected_versions = initial_selections;
    
    // Get all packages
    auto all_packages = graph.getPackages();
    for (const auto& pkg : all_packages) {
        if (state.selected_versions.find(pkg) == state.selected_versions.end()) {
            state.unassigned_packages.insert(pkg);
        }
    }
    
    state.depth = 0;
    
    // Run backtracking
    if (backtrack(state, graph, sources)) {
        result.success = true;
        result.selected_versions = state.selected_versions;
    } else {
        result.failure_reason = "No solution found";
    }
    
    return result;
}

