#pragma once

#include "source.hpp"
#include "../network/http_client.hpp"
#include "../network/cache.hpp"
#include <memory>

using namespace std;

class PyPISource : public Source {
public:
    PyPISource();
    explicit PyPISource(shared_ptr<Cache> cache);
    
    string getLanguage() const override { return "python"; }
    string getName() const override { return "PyPI"; }
    
    optional<Package> fetchPackage(const string& name, const string& version) override;
    vector<string> getAvailableVersions(const string& name) override;
    bool packageExists(const string& name) override;
    
    // Parallel fetching support
    void prefetch(const vector<string>& names) override;
    map<string, optional<Package>> fetchLatestBatch(const vector<string>& names) override;
    
private:
    unique_ptr<HttpClient> http_client;
    shared_ptr<Cache> cache;
    
    // PyPI API base URL
    static const string API_BASE_URL;
    
    // Fetch package metadata from PyPI
    optional<string> fetchPackageMetadata(const string& name);
    
    // Parse PyPI JSON response
    optional<Package> parsePackageJson(const string& json_str, const string& name, const string& version);
    
    // Extract dependencies from PyPI metadata
    vector<Dependency> extractDependencies(const string& json_str, const string& version);
};

