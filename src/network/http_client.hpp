#pragma once

#include <string>
#include <optional>
#include <vector>
#include <map>
#include <future>
#include <functional>

using namespace std;

// simple http client wrapper around libcurl
class HttpClient {
public:
    HttpClient();
    ~HttpClient();
    
    // basic get request - returns response body or nullopt on error
    optional<string> get(const string& url);
    
    // get with custom timeout
    optional<string> get(const string& url, int timeout_seconds);
    
    // fetch multiple urls at once using threads
    // max_concurrent controls how many requests run in parallel
    map<string, optional<string>> getParallel(const vector<string>& urls, int max_concurrent = 4);
    
    void setUserAgent(const string& user_agent);
    
    string getLastError() const { return last_error; }
    
private:
    string user_agent;
    string last_error;
    
    // curl callback - writes response data to a string
    static size_t writeCallback(void* contents, size_t size, size_t nmemb, string* data);
};

