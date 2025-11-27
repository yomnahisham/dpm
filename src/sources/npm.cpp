#include "npm.hpp"
#include "../core/package.hpp"
#include "../core/dependency.hpp"
#include "../json.hpp"
#include <sstream>

using namespace std;
using json = nlohmann::json;

const string NpmSource::API_BASE_URL = "https://registry.npmjs.org/";

NpmSource::NpmSource() : cache(nullptr) {
    http_client = make_unique<HttpClient>();
}

NpmSource::NpmSource(shared_ptr<Cache> cache) : cache(cache) {
    http_client = make_unique<HttpClient>();
}

optional<string> NpmSource::fetchPackageMetadata(const string& name) {
    string cache_key = "npm:" + name;
    
    // Check cache first
    if (cache) {
        auto cached = cache->get(cache_key);
        if (cached.has_value()) {
            return cached;
        }
    }
    
    // Fetch from npm registry
    string url = API_BASE_URL + name;
    auto response = http_client->get(url);
    
    if (!response.has_value()) {
        return nullopt;
    }
    
    // Cache the response
    if (cache) {
        cache->put(cache_key, response.value());
    }
    
    return response;
}

vector<string> NpmSource::getAvailableVersions(const string& name) {
    auto metadata = fetchPackageMetadata(name);
    if (!metadata.has_value()) {
        return vector<string>();
    }
    
    vector<string> versions;
    
    try {
        json data = json::parse(metadata.value());
        
        if (data.contains("versions") && data["versions"].is_object()) {
            for (auto& [version, _] : data["versions"].items()) {
                versions.push_back(version);
            }
        }
    } catch (const json::exception& e) {
        return vector<string>();
    }
    
    return versions;
}

bool NpmSource::packageExists(const string& name) {
    auto metadata = fetchPackageMetadata(name);
    if (!metadata.has_value()) {
        return false;
    }
    
    // Verify it's valid JSON with expected structure
    try {
        json data = json::parse(metadata.value());
        return data.contains("name") && data.contains("versions");
    } catch (...) {
        return false;
    }
}

optional<Package> NpmSource::fetchPackage(const string& name, const string& version) {
    auto metadata = fetchPackageMetadata(name);
    if (!metadata.has_value()) {
        return nullopt;
    }
    
    return parsePackageJson(metadata.value(), name, version);
}

optional<Package> NpmSource::parsePackageJson(const string& json_str, const string& name, const string& version) {
    try {
        json data = json::parse(json_str);
        
        if (!data.contains("versions")) {
            return nullopt;
        }
        
        Package package(name, version, "javascript");
        package.setSource("npm");
        
        // Extract dependencies for this specific version
        auto deps = extractDependencies(json_str, version);
        package.setDependencies(deps);
        
        return package;
    } catch (const json::exception& e) {
        return nullopt;
    }
}

vector<Dependency> NpmSource::extractDependencies(const string& json_str, const string& version) {
    vector<Dependency> deps;
    
    try {
        json data = json::parse(json_str);
        
        // Try to get dependencies from specific version
        if (data.contains("versions") && data["versions"].contains(version)) {
            json version_data = data["versions"][version];
            
            if (version_data.contains("dependencies") && version_data["dependencies"].is_object()) {
                for (auto& [dep_name, dep_version] : version_data["dependencies"].items()) {
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
        }
    } catch (const json::exception& e) {
        // JSON parsing failed
    }
    
    return deps;
}
