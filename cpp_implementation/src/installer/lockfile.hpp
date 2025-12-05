#pragma once

#include "../core/package.hpp"
#include "../json.hpp"
#include <string>
#include <map>
#include <vector>
#include <optional>
#include <fstream>
#include <filesystem>

using namespace std;
using json = nlohmann::json;
namespace fs = std::filesystem;

// info about a locked package
struct LockedPackage {
    string name;
    string version;
    string language;
    string source;
    vector<string> dependencies;
    string integrity;  // for future hash verification
};

// handles reading/writing dpm.lock file
// lock files ensure everyone gets the same versions
class LockFile {
public:
    static const string LOCK_FILENAME;  // "dpm.lock"
    
    LockFile() = default;
    explicit LockFile(const string& directory);
    
    bool exists() const;
    
    // read lock file from disk
    bool load();
    
    // write lock file to disk
    bool save() const;
    
    optional<LockedPackage> getPackage(const string& name) const;
    
    map<string, LockedPackage> getPackages() const { return packages; }
    
    // just the versions for quick lookup
    map<string, string> getLockedVersions() const;
    
    // populate from resolution result
    void setFromResolution(const map<string, string>& selected_versions,
                          const map<string, vector<string>>& dependencies,
                          const map<string, pair<string, string>>& package_info);
    
    void clear() { packages.clear(); }
    
    // check if a resolution matches what's in the lock file
    bool matches(const map<string, string>& selected_versions) const;
    
    string getPath() const { return lock_path; }
    
private:
    string lock_path;
    map<string, LockedPackage> packages;
    
    json toJson() const;
    bool fromJson(const json& j);
};

