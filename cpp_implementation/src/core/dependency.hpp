#pragma once

#include "version.hpp"
#include <string>
#include <vector>

using namespace std;

// a dependency is just a package name with version constraints
// like "numpy>=1.0.0" or "flask~=2.0"
class Dependency {
public:
    Dependency();
    Dependency(const string& name, const vector<VersionConstraint>& constraints);
    Dependency(const string& name, const string& constraint_str);
    
    string getName() const { return name; }
    vector<VersionConstraint> getConstraints() const { return constraints; }
    
    // checks if a version works for this dependency
    bool satisfies(const Version& version) const;
    
    // parses "numpy>=1.0.0,<2.0.0" into name and constraints
    static Dependency parse(const string& dep_str);
    
    string toString() const;
    
private:
    string name;
    vector<VersionConstraint> constraints;
};

