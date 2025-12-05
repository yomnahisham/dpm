#pragma once

#include <string>
#include <optional>

using namespace std;

// handles checksum verification for packages
// uses sha256 for integrity checks
class IntegrityChecker {
public:
    // compute sha256 hash of a string (like json response)
    static string sha256(const string& data);
    
    // compute sha256 hash of a file
    static optional<string> sha256File(const string& filepath);
    
    // format as "sha256-<base64hash>" like npm does
    static string formatIntegrity(const string& hash);
    
    // parse integrity string back to raw hash
    static optional<string> parseIntegrity(const string& integrity);
    
    // verify data against integrity string
    static bool verify(const string& data, const string& integrity);
    
    // verify file against integrity string
    static bool verifyFile(const string& filepath, const string& integrity);
};




