#pragma once

#include "source.hpp"
#include "../network/http_client.hpp"
#include "../network/cache.hpp"
#include <memory>

using namespace std;

class NpmSource : public Source {
public:
    NpmSource();
    explicit NpmSource(shared_ptr<Cache> cache);
    
    string getLanguage() const override { return "javascript"; }
    string getName() const override { return "npm"; }
    
    optional<Package> fetchPackage(const string& name, const string& version) override;
    vector<string> getAvailableVersions(const string& name) override;
    bool packageExists(const string& name) override;
    
private:
    unique_ptr<HttpClient> http_client;
    shared_ptr<Cache> cache;
    
    // npm registry API base URL
    static const string API_BASE_URL;
    
    // Fetch package metadata from npm
    optional<string> fetchPackageMetadata(const string& name);
    
    // Parse npm JSON response
    optional<Package> parsePackageJson(const string& json_str, const string& name, const string& version);
    
    // Extract dependencies from npm metadata
    vector<Dependency> extractDependencies(const string& json_str, const string& version);
};

