#include "system.hpp"
#include "../core/package.hpp"
#include <cstdlib>
#include <sstream>
#include <memory>
#include <array>
#include <cstdio>

using namespace std;

SystemSource::SystemSource() {}

string SystemSource::detectPackageManager() const {
    // Check which package manager is available
    array<string, 2> commands = {"apt", "yum"};
    
    for (const auto& cmd : commands) {
        string test_cmd = "which " + cmd + " > /dev/null 2>&1";
        if (system(test_cmd.c_str()) == 0) {
            return cmd;
        }
    }
    
    return "unknown";
}

optional<Package> SystemSource::fetchPackage(const string& name, const string& version) {
    string pm = detectPackageManager();
    
    if (pm == "apt") {
        return queryApt(name, version);
    } else if (pm == "yum") {
        return queryYum(name, version);
    }
    
    return nullopt;
}

vector<string> SystemSource::getAvailableVersions(const string& name) {
    string pm = detectPackageManager();
    
    if (pm == "apt") {
        return queryAptVersions(name);
    } else if (pm == "yum") {
        return queryYumVersions(name);
    }
    
    return vector<string>();
}

bool SystemSource::packageExists(const string& name) {
    auto versions = getAvailableVersions(name);
    return !versions.empty();
}

optional<Package> SystemSource::queryApt(const string& name, const string& version) {
    // Query apt-cache show
    string cmd = "apt-cache show " + name + " 2>/dev/null";
    array<char, 128> buffer;
    string result;
    
    unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
    if (!pipe) {
        return nullopt;
    }
    
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    
    if (result.empty()) {
        return nullopt;
    }
    
    Package package(name, version, "system");
    package.setSource("apt");
    
    // Parse apt output (simplified)
    // In production, would parse more fields
    return package;
}

vector<string> SystemSource::queryAptVersions(const string& name) {
    vector<string> versions;
    
    string cmd = "apt-cache policy " + name + " 2>/dev/null";
    array<char, 128> buffer;
    string result;
    
    unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
    if (!pipe) {
        return versions;
    }
    
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    
    // Extract version numbers from apt policy output
    // This is simplified - would need proper parsing
    versions.push_back("installed"); // Placeholder
    
    return versions;
}

optional<Package> SystemSource::queryYum(const string& name, const string& version) {
    // Similar to apt but for yum
    Package package(name, version, "system");
    package.setSource("yum");
    return package;
}

vector<string> SystemSource::queryYumVersions(const string& name) {
    vector<string> versions;
    versions.push_back("installed"); // Placeholder
    return versions;
}

