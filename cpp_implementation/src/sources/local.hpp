#pragma once

#include "source.hpp"
#include <string>
#include <fstream>

using namespace std;

class LocalSource : public Source {
public:
    LocalSource();
    explicit LocalSource(const string& base_directory);
    
    string getLanguage() const override { return "local"; }
    string getName() const override { return "Local"; }
    
    optional<Package> fetchPackage(const string& name, const string& version) override;
    vector<string> getAvailableVersions(const string& name) override;
    bool packageExists(const string& name) override;
    
    void setBaseDirectory(const string& dir) { base_directory = dir; }
    
private:
    string base_directory;
    
    // Parse package from JSON file
    optional<Package> parsePackageFile(const string& filepath);
};



