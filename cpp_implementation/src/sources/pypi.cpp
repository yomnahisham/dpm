#include "pypi.hpp"
#include "../core/package.hpp"
#include "../core/dependency.hpp"
#include "../json.hpp"
#include <sstream>
#include <regex>
#include <future>
#include <thread>

using namespace std;
using json = nlohmann::json;

const string PyPISource::API_BASE_URL = "https://pypi.org/pypi/";

PyPISource::PyPISource() : cache(nullptr) {
    http_client = make_unique<HttpClient>();
}

PyPISource::PyPISource(shared_ptr<Cache> cache) : cache(cache) {
    http_client = make_unique<HttpClient>();
}

optional<string> PyPISource::fetchPackageMetadata(const string& name) {
    string cache_key = "pypi:" + name;
    
    // Check cache first
    if (cache) {
        auto cached = cache->get(cache_key);
        if (cached.has_value()) {
            return cached;
        }
    }
    
    // Fetch from PyPI
    string url = API_BASE_URL + name + "/json";
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

vector<string> PyPISource::getAvailableVersions(const string& name) {
    auto metadata = fetchPackageMetadata(name);
    if (!metadata.has_value()) {
        return vector<string>();
    }
    
    vector<string> versions;
    
    try {
        json data = json::parse(metadata.value());
        
        if (data.contains("releases") && data["releases"].is_object()) {
            for (auto& [version, _] : data["releases"].items()) {
                versions.push_back(version);
            }
        }
    } catch (const json::exception& e) {
        // JSON parsing failed
        return vector<string>();
    }
    
    return versions;
}

bool PyPISource::packageExists(const string& name) {
    auto metadata = fetchPackageMetadata(name);
    if (!metadata.has_value()) {
        return false;
    }
    
    // Verify it's valid JSON with expected structure
    try {
        json data = json::parse(metadata.value());
        return data.contains("info") && data.contains("releases");
    } catch (...) {
        return false;
    }
}

optional<Package> PyPISource::fetchPackage(const string& name, const string& version) {
    auto metadata = fetchPackageMetadata(name);
    if (!metadata.has_value()) {
        return nullopt;
    }
    
    return parsePackageJson(metadata.value(), name, version);
}

optional<Package> PyPISource::parsePackageJson(const string& json_str, const string& name, const string& version) {
    try {
        json data = json::parse(json_str);
        
        if (!data.contains("info")) {
            return nullopt;
        }
        
        Package package(name, version, "python");
        package.setSource("PyPI");
        
        // Extract dependencies
        auto deps = extractDependencies(json_str, version);
        package.setDependencies(deps);
        
        return package;
    } catch (const json::exception& e) {
        return nullopt;
    }
}

vector<Dependency> PyPISource::extractDependencies(const string& json_str, const string& version) {
    vector<Dependency> deps;
    
    try {
        json data = json::parse(json_str);
        
        if (data.contains("info") && data["info"].contains("requires_dist") && 
            !data["info"]["requires_dist"].is_null()) {
            
            for (const auto& dep_str : data["info"]["requires_dist"]) {
                if (dep_str.is_string()) {
                    string dep_string = dep_str.get<string>();
                    
                    // Skip optional dependencies (those with "extra" markers)
                    if (dep_string.find("extra ==") != string::npos) {
                        continue;
                    }
                    
                    // Parse dependency string (e.g., "numpy>=1.0.0")
                    // Remove any markers after semicolon
                    size_t semicolon_pos = dep_string.find(';');
                    if (semicolon_pos != string::npos) {
                        dep_string = dep_string.substr(0, semicolon_pos);
                    }
                    
                    // Trim whitespace
                    dep_string.erase(0, dep_string.find_first_not_of(" \t"));
                    dep_string.erase(dep_string.find_last_not_of(" \t") + 1);
                    
                    if (!dep_string.empty()) {
                        try {
                            auto dep = Dependency::parse(dep_string);
                            deps.push_back(dep);
                        } catch (...) {
                            // Skip invalid dependencies
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

void PyPISource::prefetch(const vector<string>& names) {
    // Build URLs for packages not in cache
    vector<string> urls;
    vector<string> names_to_fetch;
    
    for (const auto& name : names) {
        string cache_key = "pypi:" + name;
        if (!cache || !cache->exists(cache_key)) {
            urls.push_back(API_BASE_URL + name + "/json");
            names_to_fetch.push_back(name);
        }
    }
    
    if (urls.empty()) return;
    
    // Parallel fetch
    auto results = http_client->getParallel(urls, 8);
    
    // Cache results
    if (cache) {
        for (size_t i = 0; i < urls.size(); i++) {
            auto it = results.find(urls[i]);
            if (it != results.end() && it->second.has_value()) {
                cache->put("pypi:" + names_to_fetch[i], it->second.value());
            }
        }
    }
}

map<string, optional<Package>> PyPISource::fetchLatestBatch(const vector<string>& names) {
    // Prefetch all packages in parallel
    prefetch(names);
    
    // Now fetch from cache (should be fast)
    map<string, optional<Package>> results;
    for (const auto& name : names) {
        results[name] = fetchLatest(name);
    }
    return results;
}
