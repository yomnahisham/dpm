#include "resolver.hpp"
#include <algorithm>

using namespace std;

DependencyResolver::DependencyResolver() : always_backtrack(false) {}

vector<string> DependencyResolver::identifyConflictRegion(const GreedyResult& greedy_result,
                                                         const vector<string>& requested_packages) {
    // Simple implementation: return packages that were successfully resolved before conflict
    // In a full implementation, would analyze the dependency graph to find connected components
    vector<string> conflict_region;
    
    // Include the conflict package and its dependencies
    if (!greedy_result.conflict_package.empty()) {
        conflict_region.push_back(greedy_result.conflict_package);
    }
    
    // Include all requested packages that depend on the conflict
    for (const auto& pkg : requested_packages) {
        conflict_region.push_back(pkg);
    }
    
    return conflict_region;
}

ResolutionResult DependencyResolver::resolve(const vector<string>& requested_packages,
                                            const vector<shared_ptr<Source>>& sources) {
    ResolutionResult result;
    result.success = false;
    result.used_backtracking = false;
    
    // Phase 1: Try greedy first (fast path)
    GreedyResult greedy_result = greedy_resolver.resolve(requested_packages, sources);
    
    // If greedy failed with "not found", don't try backtracking
    if (!greedy_result.success) {
        if (!greedy_result.not_found_packages.empty() || 
            greedy_result.conflict_reason.find("not found") != string::npos) {
            result.success = false;
            result.error_message = greedy_result.conflict_reason;
            return result;
        }
    }
    
    if (greedy_result.success && !always_backtrack) {
        result.success = true;
        result.selected_versions = greedy_result.selected_versions;
        result.used_backtracking = false;
        return result;
    }
    
    // Phase 2: Greedy failed or always_backtrack is true, use backtracking
    result.used_backtracking = true;
    
    // Extract non-conflicting selections from greedy (if any)
    map<string, string> initial_selections = greedy_result.selected_versions;
    
    // Run backtracking
    BacktrackResult backtrack_result = backtrack_resolver.resolve(
        requested_packages,
        initial_selections,
        sources
    );
    
    if (backtrack_result.success) {
        // Verify we actually resolved something
        if (backtrack_result.selected_versions.empty() && !requested_packages.empty()) {
            result.success = false;
            result.error_message = "No packages could be resolved";
            if (!greedy_result.conflict_reason.empty()) {
                result.error_message += " (" + greedy_result.conflict_reason + ")";
            }
        } else {
            result.success = true;
            result.selected_versions = backtrack_result.selected_versions;
        }
    } else {
        result.success = false;
        result.error_message = backtrack_result.failure_reason;
        if (!greedy_result.conflict_reason.empty()) {
            result.error_message += " (Greedy conflict: " + greedy_result.conflict_reason + ")";
        }
    }
    
    return result;
}
