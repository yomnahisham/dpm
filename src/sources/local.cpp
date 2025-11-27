#include "local.hpp"
#include "../core/package.hpp"
#include "../core/dependency.hpp"
#include "../json.hpp"
#include <filesystem>
#include <fstream>
#include <sstream>

using namespace std;
using json = nlohmann::json;
namespace fs = filesystem;

LocalSource::LocalSource() : base_directory(".") {}

LocalSource::LocalSource(const string& base_directory) : base_directory(base_directory) {}

optional<Package> LocalSource::fetchPackage(const string& name, const string& version) {
    // Look for package file: base_directory/name/version.json or base_directory/name.json
    string filepath1 = base_directory + "/" + name + "/" + version + ".json";
    string filepath2 = base_directory + "/" + name + ".json";
    
    if (fs::exists(filepath1)) {
        return parsePackageFile(filepath1);
    } else if (fs::exists(filepath2)) {
        return parsePackageFile(filepath2);
    }
    
    return nullopt;
}

vector<string> LocalSource::getAvailableVersions(const string& name) {
    vector<string> versions;
    
    // Check for version-specific files
    string package_dir = base_directory + "/" + name;
    if (fs::exists(package_dir) && fs::is_directory(package_dir)) {
        for (const auto& entry : fs::directory_iterator(package_dir)) {
            if (entry.path().extension() == ".json") {
                string version = entry.path().stem().string();
                versions.push_back(version);
            }
        }
    }
    
    // Check for single package file
    string package_file = base_directory + "/" + name + ".json";
    if (fs::exists(package_file)) {
        // Try to extract version from file
        auto pkg = parsePackageFile(package_file);
        if (pkg.has_value()) {
            versions.push_back(pkg->getVersion());
        }
    }
    
    return versions;
}

bool LocalSource::packageExists(const string& name) {
    string package_dir = base_directory + "/" + name;
    string package_file = base_directory + "/" + name + ".json";
    
    return fs::exists(package_dir) || fs::exists(package_file);
}

optional<Package> LocalSource::parsePackageFile(const string& filepath) {
    ifstream file(filepath);
    if (!file.is_open()) {
        return nullopt;
    }
    
    ostringstream oss;
    oss << file.rdbuf();
    string json_str = oss.str();
    
    try {
        json data = json::parse(json_str);
        
        Package package;
        package.setLanguage("local");
        package.setSource("local");
        
        // Extract name
        if (data.contains("name") && data["name"].is_string()) {
            package.setName(data["name"].get<string>());
        } else {
            return nullopt;
        }
        
        // Extract version
        if (data.contains("version") && data["version"].is_string()) {
            package.setVersion(data["version"].get<string>());
        } else {
            package.setVersion("1.0.0"); // Default
        }
        
        // Extract dependencies
        vector<Dependency> deps;
        if (data.contains("dependencies") && data["dependencies"].is_object()) {
            for (auto& [dep_name, dep_version] : data["dependencies"].items()) {
                if (dep_version.is_string()) {
                    try {
                        Dependency dep(dep_name, dep_version.get<string>());
                        deps.push_back(dep);
                    } catch (...) {
                        // Skip invalid
                    }
                }
            }
        }
        package.setDependencies(deps);
        
        return package;
    } catch (const json::exception& e) {
        return nullopt;
    }
}
