#pragma once

#include "../core/package.hpp"
#include "../json.hpp"
#include <string>
#include <map>
#include <vector>
#include <fstream>
#include <filesystem>

using namespace std;
using json = nlohmann::json;
namespace fs = filesystem;

// Tracks installed packages
class PackageState {
public:
    PackageState() : state_file("~/.dpm/installed.json") {}
    
    bool initialize() {
        string expanded = expandPath(state_file);
        string dir = fs::path(expanded).parent_path().string();
        
        try {
            if (!fs::exists(dir)) {
                fs::create_directories(dir);
            }
            load();
            return true;
        } catch (...) {
            return false;
        }
    }
    
    void addPackage(const Package& package) {
        installed[package.getName()] = {
            {"version", package.getVersion()},
            {"language", package.getLanguage()},
            {"source", package.getSource()}
        };
        save();
    }
    
    void removePackage(const string& name) {
        installed.erase(name);
        save();
    }
    
    bool isInstalled(const string& name) const {
        return installed.find(name) != installed.end();
    }
    
    optional<string> getInstalledVersion(const string& name) const {
        auto it = installed.find(name);
        if (it != installed.end() && it->second.contains("version")) {
            return it->second["version"].get<string>();
        }
        return nullopt;
    }
    
    vector<Package> getInstalledPackages() const {
        vector<Package> packages;
        for (const auto& [name, data] : installed) {
            Package pkg;
            pkg.setName(name);
            if (data.contains("version")) {
                pkg.setVersion(data["version"].get<string>());
            }
            if (data.contains("language")) {
                pkg.setLanguage(data["language"].get<string>());
            }
            if (data.contains("source")) {
                pkg.setSource(data["source"].get<string>());
            }
            packages.push_back(pkg);
        }
        return packages;
    }
    
    size_t count() const { return installed.size(); }
    
private:
    string state_file;
    map<string, json> installed;
    
    string expandPath(const string& path) const {
        if (path.empty() || path[0] != '~') {
            return path;
        }
        const char* home = getenv("HOME");
        if (!home) return path;
        return string(home) + path.substr(1);
    }
    
    void load() {
        string expanded = expandPath(state_file);
        if (!fs::exists(expanded)) {
            installed.clear();
            return;
        }
        
        ifstream file(expanded);
        if (!file.is_open()) {
            installed.clear();
            return;
        }
        
        try {
            json data = json::parse(file);
            if (data.is_object()) {
                for (auto& [key, value] : data.items()) {
                    installed[key] = value;
                }
            }
        } catch (...) {
            installed.clear();
        }
    }
    
    void save() {
        string expanded = expandPath(state_file);
        
        json data;
        for (const auto& [name, pkg_data] : installed) {
            data[name] = pkg_data;
        }
        
        ofstream file(expanded);
        if (file.is_open()) {
            file << data.dump(2);
        }
    }
};
