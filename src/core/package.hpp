#pragma once

#include "dependency.hpp"
#include <string>
#include <vector>

using namespace std;

// represents a package with name, version, and its dependencies
class Package {
public:
    Package();
    Package(const string& name, const string& version, const string& language);
    
    // basic getters
    string getName() const { return name; }
    string getVersion() const { return version; }
    string getLanguage() const { return language; }
    string getSource() const { return source; }
    vector<Dependency> getDependencies() const { return dependencies; }
    
    // setters
    void setName(const string& name) { this->name = name; }
    void setVersion(const string& version) { this->version = version; }
    void setLanguage(const string& language) { this->language = language; }
    void setSource(const string& source) { this->source = source; }
    void setDependencies(const vector<Dependency>& deps) { dependencies = deps; }
    void addDependency(const Dependency& dep) { dependencies.push_back(dep); }
    
    // returns version as a Version object for comparison
    Version getVersionObj() const;
    
    string toString() const;
    
private:
    string name;
    string version;
    string language;  // python, javascript, system, etc
    string source;    // where we got it from (pypi, npm, etc)
    vector<Dependency> dependencies;
};

