#pragma once

#include "../core/package.hpp"
#include "../core/dependency.hpp"
#include <string>
#include <vector>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>

using namespace std;

// graph of packages and their dependencies
// used for topological sort and cycle detection
class DependencyGraph {
public:
    DependencyGraph();
    
    // add a package node
    void addPackage(const Package& package);
    
    // add edge: "from" depends on "to"
    void addDependency(const string& from, const string& to);
    
    // get all package names in the graph
    vector<string> getPackages() const;
    
    // what does this package depend on?
    vector<string> getDependencies(const string& package) const;
    
    // what packages depend on this one?
    vector<string> getDependents(const string& package) const;
    
    bool hasPackage(const string& package) const;
    
    optional<Package> getPackage(const string& name) const;
    
    // returns packages in order so dependencies come before dependents
    // basically if A depends on B, B comes first
    vector<string> topologicalSort() const;
    
    // checks for circular dependencies (A->B->C->A)
    bool hasCycle() const;
    
    // returns the actual cycle if there is one
    vector<string> getCycle() const;
    
    // finds groups of packages that all depend on each other
    // uses tarjan's algorithm
    vector<vector<string>> getStronglyConnectedComponents() const;
    
    void clear();
    
    size_t size() const { return packages.size(); }
    
private:
    map<string, vector<string>> adj_list;          // package -> its dependencies
    map<string, vector<string>> reverse_adj_list;  // package -> things that depend on it
    map<string, Package> packages;                  // package metadata
    
    // colors for dfs cycle detection
    enum class Color { WHITE, GRAY, BLACK };
    bool dfsCycle(const string& node, map<string, Color>& colors, vector<string>& cycle) const;
    
    // helper for topological sort
    void dfsTopological(const string& node, set<string>& visited, vector<string>& result) const;
    
    // tarjan's algorithm for finding strongly connected components
    void tarjanDFS(const string& node, 
                   map<string, int>& index,
                   map<string, int>& lowlink,
                   vector<string>& stack,
                   map<string, bool>& on_stack,
                   int& current_index,
                   vector<vector<string>>& sccs) const;
};

