#pragma once

#include <string>
#include <vector>
#include <optional>

using namespace std;

// represents a semantic version like 1.2.3-beta+build
class Version {
public:
    Version();
    Version(const string& version_str);
    
    // tries to parse something like "1.2.3" or "2.0.0-alpha"
    bool parse(const string& version_str);
    
    // comparison stuff - needed for sorting versions
    bool operator<(const Version& other) const;
    bool operator<=(const Version& other) const;
    bool operator>(const Version& other) const;
    bool operator>=(const Version& other) const;
    bool operator==(const Version& other) const;
    bool operator!=(const Version& other) const;
    
    // getters for version parts
    int getMajor() const { return major; }
    int getMinor() const { return minor; }
    int getPatch() const { return patch; }
    string getPrerelease() const { return prerelease; }
    string getBuild() const { return build; }
    
    string toString() const;
    
    // stable means no prerelease tag like -alpha or -beta
    bool isStable() const { return prerelease.empty(); }
    
private:
    int major;
    int minor;
    int patch;
    string prerelease;  // stuff after the dash like "alpha" or "rc1"
    string build;       // stuff after the plus sign
    
    // compares prerelease strings alphabetically mostly
    int comparePrerelease(const string& a, const string& b) const;
};

// the different ways you can constrain a version
enum class ConstraintOp {
    EQ,      // == exact match
    NE,      // != not this version
    LT,      // < less than
    LE,      // <= less than or equal
    GT,      // > greater than
    GE,      // >= greater than or equal
    TILDE,   // ~ allows patch updates (1.2.x)
    CARET    // ^ allows minor updates (1.x.x)
};

// like ">=1.0.0" or "^2.3.4"
class VersionConstraint {
public:
    VersionConstraint();
    VersionConstraint(ConstraintOp op, const Version& version);
    
    // parses stuff like ">=1.0.0" or "~2.1.0"
    static optional<VersionConstraint> parse(const string& constraint_str);
    
    // handles comma separated constraints like ">=1.0.0,<2.0.0"
    static vector<VersionConstraint> parseMultiple(const string& constraints_str);
    
    // checks if a version matches this constraint
    bool satisfies(const Version& version) const;
    
    ConstraintOp getOp() const { return op; }
    Version getVersion() const { return version; }
    
    string toString() const;
    
private:
    ConstraintOp op;
    Version version;
    
    // tilde: ~1.2.3 means >=1.2.3 and <1.3.0
    bool satisfiesTilde(const Version& v) const;
    // caret: ^1.2.3 means >=1.2.3 and <2.0.0
    bool satisfiesCaret(const Version& v) const;
};

