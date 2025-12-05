#pragma once

#include "../core/package.hpp"
#include <string>
#include <vector>
#include <map>
#include <optional>

using namespace std;

class InstallationPlan {
public:
    InstallationPlan();
    
    // Add package to install
    void addPackage(const Package& package);
    
    // Get installation order (topologically sorted)
    vector<Package> getInstallationOrder() const;
    
    // Get all packages
    vector<Package> getPackages() const;
    
    // Get package by name
    optional<Package> getPackage(const string& name) const;
    
    // Clear plan
    void clear();
    
    // Get number of packages
    size_t size() const { return packages.size(); }
    
private:
    map<string, Package> packages;
    vector<string> installation_order;
    
    // Build installation order using topological sort
    void buildOrder();
};

