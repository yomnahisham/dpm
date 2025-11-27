#pragma once

#include "../core/package.hpp"
#include "../core/version.hpp"
#include <string>
#include <vector>
#include <optional>
#include <algorithm>
#include <map>

using namespace std;

// base class for package sources like pypi, npm, etc
// each source knows how to fetch packages for its ecosystem
class Source {
public:
    virtual ~Source() = default;
    
    // what language does this source handle
    virtual string getLanguage() const = 0;
    
    // name of the source (pypi, npm, etc)
    virtual string getName() const = 0;
    
    // get a specific version of a package
    virtual optional<Package> fetchPackage(const string& name, const string& version) = 0;
    
    // list all available versions
    virtual vector<string> getAvailableVersions(const string& name) = 0;
    
    // quick check if package exists
    virtual bool packageExists(const string& name) = 0;
    
    // gets the latest version - sorts all versions and picks highest
    virtual optional<Package> fetchLatest(const string& name) {
        auto versions = getAvailableVersions(name);
        if (versions.empty()) {
            return nullopt;
        }
        
        // parse and sort versions
        vector<Version> version_objs;
        for (const auto& v_str : versions) {
            try {
                version_objs.push_back(Version(v_str));
            } catch (...) {
                // skip versions we can't parse
            }
        }
        
        if (version_objs.empty()) {
            return nullopt;
        }
        
        sort(version_objs.begin(), version_objs.end());
        string latest_version = version_objs.back().toString();
        return fetchPackage(name, latest_version);
    }
    
    // for parallel fetching - override this to prefetch multiple packages at once
    virtual void prefetch(const vector<string>& names) {
        // default does nothing - subclasses can override
    }
    
    // fetch multiple packages in one go
    virtual map<string, optional<Package>> fetchLatestBatch(const vector<string>& names) {
        map<string, optional<Package>> results;
        for (const auto& name : names) {
            results[name] = fetchLatest(name);
        }
        return results;
    }
};

