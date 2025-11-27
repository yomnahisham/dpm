#pragma once

#include <string>
#include <optional>
#include <map>

using namespace std;

// caches api responses to disk so we don't spam pypi/npm
class Cache {
public:
    Cache();
    ~Cache();
    
    // sets up the cache directory (creates if needed)
    bool initialize(const string& cache_dir = "~/.dpm/cache");
    
    // get cached data - returns nullopt if not found or expired
    optional<string> get(const string& key);
    
    // store data in cache
    bool put(const string& key, const string& data);
    
    // check if something is cached
    bool exists(const string& key);
    
    // delete everything in cache
    void clear();
    
    string getCacheDir() const { return cache_directory; }
    
private:
    string cache_directory;
    map<string, string> memory_cache;  // also keep stuff in memory for speed
    
    // turns cache key into a file path
    string getCachePath(const string& key) const;
    
    // replaces ~ with actual home directory
    string expandPath(const string& path) const;
};

