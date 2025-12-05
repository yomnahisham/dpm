#include "plan.hpp"
#include "../resolver/graph.hpp"
#include <algorithm>

using namespace std;

InstallationPlan::InstallationPlan() {}

void InstallationPlan::addPackage(const Package& package) {
    packages[package.getName()] = package;
    buildOrder();
}

vector<Package> InstallationPlan::getInstallationOrder() const {
    vector<Package> result;
    for (const auto& name : installation_order) {
        auto it = packages.find(name);
        if (it != packages.end()) {
            result.push_back(it->second);
        }
    }
    return result;
}

vector<Package> InstallationPlan::getPackages() const {
    vector<Package> result;
    for (const auto& pair : packages) {
        result.push_back(pair.second);
    }
    return result;
}

optional<Package> InstallationPlan::getPackage(const string& name) const {
    auto it = packages.find(name);
    if (it != packages.end()) {
        return it->second;
    }
    return nullopt;
}

void InstallationPlan::clear() {
    packages.clear();
    installation_order.clear();
}

void InstallationPlan::buildOrder() {
    // Build dependency graph
    DependencyGraph graph;
    
    for (const auto& pair : packages) {
        graph.addPackage(pair.second);
        
        // Add dependency edges
        for (const auto& dep : pair.second.getDependencies()) {
            string dep_name = dep.getName();
            if (packages.find(dep_name) != packages.end()) {
                graph.addDependency(pair.first, dep_name);
            }
        }
    }
    
    // Topological sort
    installation_order = graph.topologicalSort();
}



