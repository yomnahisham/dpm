#pragma once

#include "source.hpp"
#include <string>

using namespace std;

class SystemSource : public Source {
public:
    SystemSource();
    
    string getLanguage() const override { return "system"; }
    string getName() const override { return "System"; }
    
    optional<Package> fetchPackage(const string& name, const string& version) override;
    vector<string> getAvailableVersions(const string& name) override;
    bool packageExists(const string& name) override;
    
private:
    // Detect system package manager
    string detectPackageManager() const;
    
    // Query apt (Debian/Ubuntu)
    optional<Package> queryApt(const string& name, const string& version);
    vector<string> queryAptVersions(const string& name);
    
    // Query yum/dnf (RedHat/CentOS/Fedora)
    optional<Package> queryYum(const string& name, const string& version);
    vector<string> queryYumVersions(const string& name);
};

