#include "http_client.hpp"
#include <curl/curl.h>
#include <sstream>
#include <thread>
#include <mutex>

using namespace std;

HttpClient::HttpClient() : user_agent("DPM/1.0.0") {
    curl_global_init(CURL_GLOBAL_DEFAULT);
}

HttpClient::~HttpClient() {
    curl_global_cleanup();
}

size_t HttpClient::writeCallback(void* contents, size_t size, size_t nmemb, string* data) {
    size_t total_size = size * nmemb;
    data->append((char*)contents, total_size);
    return total_size;
}

optional<string> HttpClient::get(const string& url) {
    return get(url, 30); // Default 30 second timeout
}

optional<string> HttpClient::get(const string& url, int timeout_seconds) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        last_error = "Failed to initialize CURL";
        return nullopt;
    }
    
    string response_data;
    
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout_seconds);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, user_agent.c_str());
    
    CURLcode res = curl_easy_perform(curl);
    
    long response_code;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
    
    curl_easy_cleanup(curl);
    
    if (res != CURLE_OK) {
        last_error = "CURL error: " + string(curl_easy_strerror(res));
        return nullopt;
    }
    
    if (response_code != 200) {
        last_error = "HTTP error: " + to_string(response_code);
        return nullopt;
    }
    
    return response_data;
}

void HttpClient::setUserAgent(const string& user_agent) {
    this->user_agent = user_agent;
}

map<string, optional<string>> HttpClient::getParallel(const vector<string>& urls, int max_concurrent) {
    map<string, optional<string>> results;
    mutex results_mutex;
    
    // Process URLs in batches
    for (size_t i = 0; i < urls.size(); i += max_concurrent) {
        vector<future<pair<string, optional<string>>>> futures;
        
        size_t batch_end = min(i + max_concurrent, urls.size());
        for (size_t j = i; j < batch_end; j++) {
            const string& url = urls[j];
            futures.push_back(async(launch::async, [this, url]() {
                return make_pair(url, this->get(url));
            }));
        }
        
        // Collect results
        for (auto& f : futures) {
            auto result = f.get();
            lock_guard<mutex> lock(results_mutex);
            results[result.first] = result.second;
        }
    }
    
    return results;
}

