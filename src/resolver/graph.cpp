#include "graph.hpp"
#include <algorithm>
#include <stack>

using namespace std;

DependencyGraph::DependencyGraph() {}

void DependencyGraph::addPackage(const Package& package) {
    string name = package.getName();
    packages[name] = package;
    
    // Initialize adjacency lists if needed
    if (adj_list.find(name) == adj_list.end()) {
        adj_list[name] = vector<string>();
    }
    if (reverse_adj_list.find(name) == reverse_adj_list.end()) {
        reverse_adj_list[name] = vector<string>();
    }
}

void DependencyGraph::addDependency(const string& from, const string& to) {
    // Add to forward adjacency list
    if (adj_list.find(from) == adj_list.end()) {
        adj_list[from] = vector<string>();
    }
    adj_list[from].push_back(to);
    
    // Add to reverse adjacency list
    if (reverse_adj_list.find(to) == reverse_adj_list.end()) {
        reverse_adj_list[to] = vector<string>();
    }
    reverse_adj_list[to].push_back(from);
}

vector<string> DependencyGraph::getPackages() const {
    vector<string> result;
    for (const auto& pair : packages) {
        result.push_back(pair.first);
    }
    return result;
}

vector<string> DependencyGraph::getDependencies(const string& package) const {
    auto it = adj_list.find(package);
    if (it != adj_list.end()) {
        return it->second;
    }
    return vector<string>();
}

vector<string> DependencyGraph::getDependents(const string& package) const {
    auto it = reverse_adj_list.find(package);
    if (it != reverse_adj_list.end()) {
        return it->second;
    }
    return vector<string>();
}

bool DependencyGraph::hasPackage(const string& package) const {
    return packages.find(package) != packages.end();
}

optional<Package> DependencyGraph::getPackage(const string& name) const {
    auto it = packages.find(name);
    if (it != packages.end()) {
        return it->second;
    }
    return nullopt;
}

vector<string> DependencyGraph::topologicalSort() const {
    vector<string> result;
    set<string> visited;
    
    // DFS-based topological sort
    for (const auto& pair : packages) {
        if (visited.find(pair.first) == visited.end()) {
            dfsTopological(pair.first, visited, result);
        }
    }
    
    // Reverse to get correct order (dependencies first)
    reverse(result.begin(), result.end());
    return result;
}

void DependencyGraph::dfsTopological(const string& node, set<string>& visited, vector<string>& result) const {
    visited.insert(node);
    
    // Visit all dependencies first
    auto deps = getDependencies(node);
    for (const auto& dep : deps) {
        if (visited.find(dep) == visited.end()) {
            dfsTopological(dep, visited, result);
        }
    }
    
    // Add node after dependencies
    result.push_back(node);
}

bool DependencyGraph::hasCycle() const {
    map<string, Color> colors;
    
    // Initialize all nodes as white
    for (const auto& pair : packages) {
        colors[pair.first] = Color::WHITE;
    }
    
    // Check each node
    for (const auto& pair : packages) {
        if (colors[pair.first] == Color::WHITE) {
            vector<string> cycle;
            if (dfsCycle(pair.first, colors, cycle)) {
                return true;
            }
        }
    }
    
    return false;
}

vector<string> DependencyGraph::getCycle() const {
    map<string, Color> colors;
    vector<string> cycle;
    
    // Initialize all nodes as white
    for (const auto& pair : packages) {
        colors[pair.first] = Color::WHITE;
    }
    
    // Find cycle
    for (const auto& pair : packages) {
        if (colors[pair.first] == Color::WHITE) {
            if (dfsCycle(pair.first, colors, cycle)) {
                return cycle;
            }
        }
    }
    
    return vector<string>();
}

bool DependencyGraph::dfsCycle(const string& node, map<string, Color>& colors, vector<string>& cycle) const {
    colors[node] = Color::GRAY;
    cycle.push_back(node);
    
    auto deps = getDependencies(node);
    for (const auto& dep : deps) {
        if (colors[dep] == Color::GRAY) {
            // Found back edge - cycle detected
            return true;
        } else if (colors[dep] == Color::WHITE) {
            if (dfsCycle(dep, colors, cycle)) {
                return true;
            }
        }
    }
    
    colors[node] = Color::BLACK;
    cycle.pop_back();
    return false;
}

vector<vector<string>> DependencyGraph::getStronglyConnectedComponents() const {
    map<string, int> index;
    map<string, int> lowlink;
    vector<string> stack;
    map<string, bool> on_stack;
    int current_index = 0;
    vector<vector<string>> sccs;
    
    // Initialize
    for (const auto& pair : packages) {
        index[pair.first] = -1;
        lowlink[pair.first] = -1;
        on_stack[pair.first] = false;
    }
    
    // Run Tarjan's algorithm
    for (const auto& pair : packages) {
        if (index[pair.first] == -1) {
            tarjanDFS(pair.first, index, lowlink, stack, on_stack, current_index, sccs);
        }
    }
    
    return sccs;
}

void DependencyGraph::tarjanDFS(const string& node,
                                map<string, int>& index,
                                map<string, int>& lowlink,
                                vector<string>& stack,
                                map<string, bool>& on_stack,
                                int& current_index,
                                vector<vector<string>>& sccs) const {
    index[node] = current_index;
    lowlink[node] = current_index;
    current_index++;
    stack.push_back(node);
    on_stack[node] = true;
    
    auto deps = getDependencies(node);
    for (const auto& dep : deps) {
        if (index[dep] == -1) {
            tarjanDFS(dep, index, lowlink, stack, on_stack, current_index, sccs);
            lowlink[node] = min(lowlink[node], lowlink[dep]);
        } else if (on_stack[dep]) {
            lowlink[node] = min(lowlink[node], index[dep]);
        }
    }
    
    if (lowlink[node] == index[node]) {
        vector<string> scc;
        string w;
        do {
            w = stack.back();
            stack.pop_back();
            on_stack[w] = false;
            scc.push_back(w);
        } while (w != node);
        sccs.push_back(scc);
    }
}

void DependencyGraph::clear() {
    adj_list.clear();
    reverse_adj_list.clear();
    packages.clear();
}

