#include "dependency.hpp"
#include <sstream>
#include <algorithm>
#include <regex>

using namespace std;

Dependency::Dependency() {}

Dependency::Dependency(const string& name, const vector<VersionConstraint>& constraints)
    : name(name), constraints(constraints) {}

Dependency::Dependency(const string& name, const string& constraint_str)
    : name(name) {
    constraints = VersionConstraint::parseMultiple(constraint_str);
}

bool Dependency::satisfies(const Version& version) const {
    if (constraints.empty()) {
        return true; // No constraints means any version
    }
    
    // All constraints must be satisfied
    for (const auto& constraint : constraints) {
        if (!constraint.satisfies(version)) {
            return false;
        }
    }
    return true;
}

Dependency Dependency::parse(const string& dep_str) {
    // Format: "name>=1.0.0,<2.0.0" or "name (>=1.0.0)" or "name[extra]>=1.0.0"
    string trimmed = dep_str;
    trimmed.erase(0, trimmed.find_first_not_of(" \t"));
    trimmed.erase(trimmed.find_last_not_of(" \t") + 1);
    
    if (trimmed.empty()) {
        return Dependency("", vector<VersionConstraint>());
    }
    
    // Remove extras like [security] or (>=1.0.0)
    size_t bracket_pos = trimmed.find('[');
    if (bracket_pos != string::npos) {
        size_t close_bracket = trimmed.find(']', bracket_pos);
        if (close_bracket != string::npos) {
            trimmed = trimmed.substr(0, bracket_pos) + trimmed.substr(close_bracket + 1);
        }
    }
    
    // Remove parentheses
    size_t paren_pos = trimmed.find('(');
    if (paren_pos != string::npos) {
        size_t close_paren = trimmed.find(')', paren_pos);
        if (close_paren != string::npos) {
            string inside = trimmed.substr(paren_pos + 1, close_paren - paren_pos - 1);
            trimmed = trimmed.substr(0, paren_pos) + inside;
        }
    }
    
    // Trim again
    trimmed.erase(0, trimmed.find_first_not_of(" \t"));
    trimmed.erase(trimmed.find_last_not_of(" \t") + 1);
    
    // Find where the package name ends and version constraint begins
    // Package names are alphanumeric with - and _
    size_t constraint_start = string::npos;
    
    for (size_t i = 0; i < trimmed.size(); ++i) {
        char c = trimmed[i];
        if (c == '>' || c == '<' || c == '=' || c == '!' || c == '~' || c == '^') {
            constraint_start = i;
            break;
        }
        if (c == ' ' || c == '\t') {
            // Check if next non-whitespace is a constraint operator
            size_t next = trimmed.find_first_not_of(" \t", i);
            if (next != string::npos) {
                char nc = trimmed[next];
                if (nc == '>' || nc == '<' || nc == '=' || nc == '!' || nc == '~' || nc == '^') {
                    constraint_start = next;
                    break;
                }
            }
            constraint_start = i;
            break;
        }
    }
    
    if (constraint_start == string::npos || constraint_start == 0) {
        // No constraints or empty name
        return Dependency(trimmed, vector<VersionConstraint>());
    }
    
    string name = trimmed.substr(0, constraint_start);
    string constraints_str = trimmed.substr(constraint_start);
    
    // Trim name and constraints
    name.erase(0, name.find_first_not_of(" \t"));
    name.erase(name.find_last_not_of(" \t") + 1);
    constraints_str.erase(0, constraints_str.find_first_not_of(" \t"));
    constraints_str.erase(constraints_str.find_last_not_of(" \t") + 1);
    
    return Dependency(name, constraints_str);
}

string Dependency::toString() const {
    ostringstream oss;
    oss << name;
    if (!constraints.empty()) {
        for (size_t i = 0; i < constraints.size(); ++i) {
            if (i > 0) oss << ",";
            oss << constraints[i].toString();
        }
    }
    return oss.str();
}
