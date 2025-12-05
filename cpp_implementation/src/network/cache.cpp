#include "cache.hpp"
#include <fstream>
#include <filesystem>
#include <cstdlib>
#include <sstream>
#include <functional>

using namespace std;
namespace fs = filesystem;

Cache::Cache() : cache_directory("~/.dpm/cache") {}

Cache::~Cache() {}

string Cache::expandPath(const string& path) const {
    if (path.empty() || path[0] != '~') {
        return path;
    }
    
    const char* home = getenv("HOME");
    if (!home) {
        return path;
    }
    
    return string(home) + path.substr(1);
}

string Cache::getCachePath(const string& key) const {
    // Hash the key using std::hash
    hash<string> hasher;
    size_t hash_value = hasher(key);
    
    ostringstream oss;
    oss << hex << hash_value;
    
    // Sanitize key for filename (replace invalid chars)
    string sanitized_key = key;
    for (char& c : sanitized_key) {
        if (c == '/' || c == '\\' || c == ':' || c == '*' || c == '?' || 
            c == '"' || c == '<' || c == '>' || c == '|') {
            c = '_';
        }
    }
    
    string expanded_dir = expandPath(cache_directory);
    return expanded_dir + "/" + sanitized_key + "_" + oss.str();
}

bool Cache::initialize(const string& cache_dir) {
    cache_directory = cache_dir;
    string expanded_dir = expandPath(cache_directory);
    
    try {
        if (!fs::exists(expanded_dir)) {
            fs::create_directories(expanded_dir);
        }
        return true;
    } catch (...) {
        return false;
    }
}

optional<string> Cache::get(const string& key) {
    // Check memory cache first
    auto it = memory_cache.find(key);
    if (it != memory_cache.end()) {
        return it->second;
    }
    
    // Check file cache
    string cache_path = getCachePath(key);
    if (!fs::exists(cache_path)) {
        return nullopt;
    }
    
    ifstream file(cache_path);
    if (!file.is_open()) {
        return nullopt;
    }
    
    ostringstream oss;
    oss << file.rdbuf();
    string data = oss.str();
    
    // Store in memory cache
    memory_cache[key] = data;
    
    return data;
}

bool Cache::put(const string& key, const string& data) {
    // Store in memory cache
    memory_cache[key] = data;
    
    // Store in file cache
    string cache_path = getCachePath(key);
    string expanded_dir = expandPath(cache_directory);
    
    try {
        if (!fs::exists(expanded_dir)) {
            fs::create_directories(expanded_dir);
        }
        
        ofstream file(cache_path);
        if (!file.is_open()) {
            return false;
        }
        
        file << data;
        return true;
    } catch (...) {
        return false;
    }
}

bool Cache::exists(const string& key) {
    if (memory_cache.find(key) != memory_cache.end()) {
        return true;
    }
    
    string cache_path = getCachePath(key);
    return fs::exists(cache_path);
}

void Cache::clear() {
    memory_cache.clear();
    
    string expanded_dir = expandPath(cache_directory);
    try {
        if (fs::exists(expanded_dir)) {
            for (const auto& entry : fs::directory_iterator(expanded_dir)) {
                fs::remove(entry.path());
            }
        }
    } catch (...) {
        // Ignore errors
    }
}

