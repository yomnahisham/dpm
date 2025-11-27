#include "greedy.hpp"
#include "../core/dependency.hpp"
#include <algorithm>
#include <sstream>

using namespace std;

GreedyResolver::GreedyResolver() {}

pair<DependencyGraph, vector<string>> GreedyResolver::buildGraphWithErrors(
    const vector<string>& requested_packages,
    const vector<shared_ptr<Source>>& sources) {
    
    DependencyGraph graph;
    vector<string> not_found;
    
    // Queue for BFS traversal
    vector<string> queue = requested_packages;
    map<string, bool> processed;
    
    // Prefetch initial packages in parallel
    for (const auto& source : sources) {
        source->prefetch(requested_packages);
    }
    
    while (!queue.empty()) {
        // Batch process: collect unprocessed packages
        vector<string> batch;
        while (!queue.empty() && batch.size() < 10) {
            string pkg = queue.back();
            queue.pop_back();
            if (!processed[pkg]) {
                batch.push_back(pkg);
                processed[pkg] = true;
            }
        }
        
        if (batch.empty()) continue;
        
        // Prefetch batch dependencies
        for (const auto& source : sources) {
            source->prefetch(batch);
        }
        
        // Process batch
        for (const auto& package_name : batch) {
            // Find source for this package
            shared_ptr<Source> source = nullptr;
            for (const auto& s : sources) {
                if (s->packageExists(package_name)) {
                    source = s;
                    break;
                }
            }
            
            if (!source) {
                not_found.push_back(package_name);
                continue;
            }
            
            // Get latest version (greedy: try latest first)
            auto package_opt = source->fetchLatest(package_name);
            if (!package_opt.has_value()) {
                not_found.push_back(package_name);
                continue;
            }
            
            Package package = package_opt.value();
            graph.addPackage(package);
            
            // Collect dependencies for next batch prefetch
            vector<string> deps_to_prefetch;
            for (const auto& dep : package.getDependencies()) {
                string dep_name = dep.getName();
                graph.addDependency(package_name, dep_name);
                
                if (!processed[dep_name]) {
                    queue.push_back(dep_name);
                    deps_to_prefetch.push_back(dep_name);
                }
            }
            
            // Prefetch dependencies
            if (!deps_to_prefetch.empty()) {
                for (const auto& s : sources) {
                    s->prefetch(deps_to_prefetch);
                }
            }
        }
    }
    
    return {graph, not_found};
}

vector<VersionConstraint> GreedyResolver::getConstraints(const string& package,
                                                        const DependencyGraph& graph) {
    vector<VersionConstraint> constraints;
    
    // Get all dependents (packages that depend on this one)
    auto dependents = graph.getDependents(package);
    
    for (const auto& dependent : dependents) {
        auto dep_package_opt = graph.getPackage(dependent);
        if (!dep_package_opt.has_value()) {
            continue;
        }
        
        Package dep_package = dep_package_opt.value();
        
        // Find constraint for this package in dependent's dependencies
        for (const auto& dep : dep_package.getDependencies()) {
            if (dep.getName() == package) {
                auto dep_constraints = dep.getConstraints();
                constraints.insert(constraints.end(), 
                                 dep_constraints.begin(), 
                                 dep_constraints.end());
            }
        }
    }
    
    return constraints;
}

int GreedyResolver::scoreVersion(const Version& version,
                                 [[maybe_unused]] const vector<VersionConstraint>& constraints,
                                 const map<string, string>& selected) {
    int score = 0;
    
    // Prefer stable versions
    if (version.isStable()) {
        score += 1000;
    }
    
    // Prefer newer versions (higher major/minor/patch)
    score += version.getMajor() * 100;
    score += version.getMinor() * 10;
    score += version.getPatch();
    
    // Check if this version is already selected (reuse optimization)
    for (const auto& pair : selected) {
        try {
            Version selected_version(pair.second);
            if (selected_version == version) {
                score += 500; // Bonus for reusing
            }
        } catch (...) {
            // Ignore
        }
    }
    
    return score;
}

optional<string> GreedyResolver::selectBestVersion([[maybe_unused]] const string& package,
                                                  const vector<string>& available_versions,
                                                  const vector<VersionConstraint>& constraints,
                                                  [[maybe_unused]] const vector<shared_ptr<Source>>& sources) {
    vector<pair<Version, string>> valid_versions; // (version_obj, version_str)
    
    // Filter versions by constraints
    for (const auto& version_str : available_versions) {
        try {
            Version version(version_str);
            
            // Check if version satisfies all constraints
            bool satisfies_all = true;
            for (const auto& constraint : constraints) {
                if (!constraint.satisfies(version)) {
                    satisfies_all = false;
                    break;
                }
            }
            
            if (satisfies_all) {
                valid_versions.push_back({version, version_str});
            }
        } catch (...) {
            // Skip invalid versions
        }
    }
    
    if (valid_versions.empty()) {
        return nullopt;
    }
    
    // Sort by score (greedy heuristic)
    sort(valid_versions.begin(), valid_versions.end(),
         [this, &constraints](const pair<Version, string>& a,
                              const pair<Version, string>& b) {
             int score_a = scoreVersion(a.first, constraints, selected_versions);
             int score_b = scoreVersion(b.first, constraints, selected_versions);
             return score_a > score_b; // Higher score is better
         });
    
    return valid_versions[0].second;
}

GreedyResult GreedyResolver::resolve(const vector<string>& requested_packages,
                                    const vector<shared_ptr<Source>>& sources) {
    selected_versions.clear();
    GreedyResult result;
    result.success = false;
    
    // Build dependency graph
    auto [graph, not_found] = buildGraphWithErrors(requested_packages, sources);
    result.not_found_packages = not_found;
    
    // If any requested package was not found, fail immediately
    for (const auto& pkg : requested_packages) {
        bool found = false;
        for (const auto& nf : not_found) {
            if (nf == pkg) {
                found = true;
                break;
            }
        }
        if (found) {
            result.conflict_package = pkg;
            result.conflict_reason = "Package not found in any source: " + pkg;
            return result;
        }
    }
    
    // Check for cycles
    if (graph.hasCycle()) {
        result.conflict_reason = "Circular dependency detected";
        auto cycle = graph.getCycle();
        if (!cycle.empty()) {
            result.conflict_package = cycle[0];
        }
        return result;
    }
    
    // Topological sort to get resolution order
    vector<string> resolution_order = graph.topologicalSort();
    
    // Resolve each package in order
    for (const auto& package_name : resolution_order) {
        // Find source for this package
        shared_ptr<Source> source = nullptr;
        for (const auto& s : sources) {
            if (s->packageExists(package_name)) {
                source = s;
                break;
            }
        }
        
        if (!source) {
            result.conflict_package = package_name;
            result.conflict_reason = "Package not found in any source: " + package_name;
            return result;
        }
        
        // Get available versions
        vector<string> available_versions = source->getAvailableVersions(package_name);
        if (available_versions.empty()) {
            result.conflict_package = package_name;
            result.conflict_reason = "No versions available for: " + package_name;
            return result;
        }
        
        // Get constraints from dependents
        vector<VersionConstraint> constraints = getConstraints(package_name, graph);
        
        // Select best version using greedy heuristics
        auto best_version = selectBestVersion(package_name, available_versions, 
                                             constraints, sources);
        
        if (!best_version.has_value()) {
            result.conflict_package = package_name;
            result.conflict_reason = "No version satisfies constraints for: " + package_name;
            return result;
        }
        
        selected_versions[package_name] = best_version.value();
    }
    
    result.success = true;
    result.selected_versions = selected_versions;
    return result;
}
