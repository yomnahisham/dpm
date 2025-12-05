#include "lockfile.hpp"
#include "../core/logger.hpp"
#include <iomanip>

using namespace std;

#define LOG_ERROR(msg) Logger::instance().error(msg)

const string LockFile::LOCK_FILENAME = "dpm.lock";

LockFile::LockFile(const string& directory) {
    lock_path = (fs::path(directory) / LOCK_FILENAME).string();
}

bool LockFile::exists() const {
    return fs::exists(lock_path);
}

bool LockFile::load() {
    if (!exists()) {
        return false;
    }
    
    try {
        ifstream file(lock_path);
        if (!file.is_open()) {
            LOG_ERROR("Failed to open lock file: " + lock_path);
            return false;
        }
        
        json j;
        file >> j;
        return fromJson(j);
    } catch (const exception& e) {
        LOG_ERROR("Failed to parse lock file: " + string(e.what()));
        return false;
    }
}

bool LockFile::save() const {
    try {
        // Create directory if needed
        fs::path dir = fs::path(lock_path).parent_path();
        if (!dir.empty() && !fs::exists(dir)) {
            fs::create_directories(dir);
        }
        
        ofstream file(lock_path);
        if (!file.is_open()) {
            LOG_ERROR("Failed to create lock file: " + lock_path);
            return false;
        }
        
        file << setw(2) << toJson() << endl;
        return true;
    } catch (const exception& e) {
        LOG_ERROR("Failed to write lock file: " + string(e.what()));
        return false;
    }
}

optional<LockedPackage> LockFile::getPackage(const string& name) const {
    auto it = packages.find(name);
    if (it != packages.end()) {
        return it->second;
    }
    return nullopt;
}

map<string, string> LockFile::getLockedVersions() const {
    map<string, string> versions;
    for (const auto& [name, pkg] : packages) {
        versions[name] = pkg.version;
    }
    return versions;
}

void LockFile::setFromResolution(const map<string, string>& selected_versions,
                                 const map<string, vector<string>>& dependencies,
                                 const map<string, pair<string, string>>& package_info) {
    packages.clear();
    
    for (const auto& [name, version] : selected_versions) {
        LockedPackage pkg;
        pkg.name = name;
        pkg.version = version;
        
        // Get language and source
        auto info_it = package_info.find(name);
        if (info_it != package_info.end()) {
            pkg.language = info_it->second.first;
            pkg.source = info_it->second.second;
        }
        
        // Get dependencies
        auto deps_it = dependencies.find(name);
        if (deps_it != dependencies.end()) {
            pkg.dependencies = deps_it->second;
        }
        
        packages[name] = pkg;
    }
}

bool LockFile::matches(const map<string, string>& selected_versions) const {
    if (packages.size() != selected_versions.size()) {
        return false;
    }
    
    for (const auto& [name, version] : selected_versions) {
        auto it = packages.find(name);
        if (it == packages.end() || it->second.version != version) {
            return false;
        }
    }
    return true;
}

json LockFile::toJson() const {
    json j;
    j["version"] = 1;  // Lock file format version
    j["packages"] = json::object();
    
    for (const auto& [name, pkg] : packages) {
        json pkg_json;
        pkg_json["version"] = pkg.version;
        pkg_json["language"] = pkg.language;
        pkg_json["source"] = pkg.source;
        pkg_json["dependencies"] = pkg.dependencies;
        if (!pkg.integrity.empty()) {
            pkg_json["integrity"] = pkg.integrity;
        }
        j["packages"][name] = pkg_json;
    }
    
    return j;
}

bool LockFile::fromJson(const json& j) {
    try {
        packages.clear();
        
        if (!j.contains("packages") || !j["packages"].is_object()) {
            return false;
        }
        
        for (auto& [name, pkg_json] : j["packages"].items()) {
            LockedPackage pkg;
            pkg.name = name;
            pkg.version = pkg_json.value("version", "");
            pkg.language = pkg_json.value("language", "");
            pkg.source = pkg_json.value("source", "");
            pkg.integrity = pkg_json.value("integrity", "");
            
            if (pkg_json.contains("dependencies") && pkg_json["dependencies"].is_array()) {
                for (const auto& dep : pkg_json["dependencies"]) {
                    pkg.dependencies.push_back(dep.get<string>());
                }
            }
            
            packages[name] = pkg;
        }
        
        return true;
    } catch (const exception& e) {
        LOG_ERROR("Failed to parse lock file JSON: " + string(e.what()));
        return false;
    }
}

