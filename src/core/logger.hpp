#pragma once

#include <string>
#include <iostream>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <sstream>

using namespace std;

enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR
};

class Logger {
public:
    static Logger& instance() {
        static Logger logger;
        return logger;
    }
    
    void setLevel(LogLevel level) { current_level = level; }
    void setQuiet(bool q) { quiet = q; }
    void setLogFile(const string& filepath) {
        if (log_file.is_open()) {
            log_file.close();
        }
        log_file.open(filepath, ios::app);
    }
    
    void debug(const string& message) { log(LogLevel::DEBUG, message); }
    void info(const string& message) { log(LogLevel::INFO, message); }
    void warning(const string& message) { log(LogLevel::WARNING, message); }
    void error(const string& message) { log(LogLevel::ERROR, message); }
    
    void log(LogLevel level, const string& message) {
        if (level < current_level) return;
        
        string level_str;
        switch (level) {
            case LogLevel::DEBUG: level_str = "DEBUG"; break;
            case LogLevel::INFO: level_str = "INFO"; break;
            case LogLevel::WARNING: level_str = "WARN"; break;
            case LogLevel::ERROR: level_str = "ERROR"; break;
        }
        
        auto now = chrono::system_clock::now();
        auto time = chrono::system_clock::to_time_t(now);
        
        ostringstream oss;
        oss << "[" << put_time(localtime(&time), "%Y-%m-%d %H:%M:%S") << "] "
            << "[" << level_str << "] " << message;
        
        string log_line = oss.str();
        
        // Output to console only if not quiet
        if (!quiet) {
            if (level >= LogLevel::WARNING) {
                cerr << log_line << endl;
            }
        }
        
        // Output to file if configured
        if (log_file.is_open()) {
            log_file << log_line << endl;
            log_file.flush();
        }
    }
    
private:
    Logger() : current_level(LogLevel::INFO), quiet(true) {}  // quiet by default
    ~Logger() {
        if (log_file.is_open()) {
            log_file.close();
        }
    }
    
    LogLevel current_level;
    bool quiet;
    ofstream log_file;
};

#define LOG_DEBUG(msg) Logger::instance().debug(msg)
#define LOG_INFO(msg) Logger::instance().info(msg)
#define LOG_WARN(msg) Logger::instance().warning(msg)
#define LOG_ERROR(msg) Logger::instance().error(msg)
