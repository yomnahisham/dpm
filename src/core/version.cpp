#include "version.hpp"
#include <sstream>
#include <regex>
#include <algorithm>
#include <stdexcept>

using namespace std;

// Version implementation
Version::Version() : major(0), minor(0), patch(0) {}

Version::Version(const string& version_str) : major(0), minor(0), patch(0) {
    if (!parse(version_str)) {
        throw invalid_argument("Invalid version string: " + version_str);
    }
}

bool Version::parse(const string& version_str) {
    // Try full semver first: major.minor.patch[-prerelease][+build]
    regex semver_regex(R"(^(\d+)\.(\d+)\.(\d+)(?:-([\w\.-]+))?(?:\+([\w\.-]+))?$)");
    smatch matches;
    
    if (regex_match(version_str, matches, semver_regex)) {
        try {
            major = stoi(matches[1].str());
            minor = stoi(matches[2].str());
            patch = stoi(matches[3].str());
            prerelease = matches[4].str();
            build = matches[5].str();
            return true;
        } catch (...) {
            return false;
        }
    }
    
    // Try major.minor format (e.g., "14.0", "15.3")
    regex two_part_regex(R"(^(\d+)\.(\d+)(?:-([\w\.-]+))?(?:\+([\w\.-]+))?$)");
    if (regex_match(version_str, matches, two_part_regex)) {
        try {
            major = stoi(matches[1].str());
            minor = stoi(matches[2].str());
            patch = 0;
            prerelease = matches[3].str();
            build = matches[4].str();
            return true;
        } catch (...) {
            return false;
        }
    }
    
    // Try single number (e.g., "2024")
    regex single_regex(R"(^(\d+)(?:-([\w\.-]+))?(?:\+([\w\.-]+))?$)");
    if (regex_match(version_str, matches, single_regex)) {
        try {
            major = stoi(matches[1].str());
            minor = 0;
            patch = 0;
            prerelease = matches[2].str();
            build = matches[3].str();
            return true;
        } catch (...) {
            return false;
        }
    }
    
    return false;
}

bool Version::operator<(const Version& other) const {
    if (major != other.major) return major < other.major;
    if (minor != other.minor) return minor < other.minor;
    if (patch != other.patch) return patch < other.patch;
    
    // Compare prerelease: stable > prerelease, then lexicographic
    if (prerelease.empty() && !other.prerelease.empty()) return false;
    if (!prerelease.empty() && other.prerelease.empty()) return true;
    if (!prerelease.empty() && !other.prerelease.empty()) {
        return comparePrerelease(prerelease, other.prerelease) < 0;
    }
    
    return false;
}

bool Version::operator<=(const Version& other) const {
    return *this < other || *this == other;
}

bool Version::operator>(const Version& other) const {
    return other < *this;
}

bool Version::operator>=(const Version& other) const {
    return *this > other || *this == other;
}

bool Version::operator==(const Version& other) const {
    return major == other.major && 
           minor == other.minor && 
           patch == other.patch &&
           prerelease == other.prerelease;
}

bool Version::operator!=(const Version& other) const {
    return !(*this == other);
}

string Version::toString() const {
    ostringstream oss;
    oss << major << "." << minor << "." << patch;
    if (!prerelease.empty()) {
        oss << "-" << prerelease;
    }
    if (!build.empty()) {
        oss << "+" << build;
    }
    return oss.str();
}

int Version::comparePrerelease(const string& a, const string& b) const {
    // Simple lexicographic comparison
    // Could be enhanced to handle numeric parts (e.g., "alpha.1" vs "alpha.2")
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

// VersionConstraint implementation
VersionConstraint::VersionConstraint() : op(ConstraintOp::EQ) {}

VersionConstraint::VersionConstraint(ConstraintOp op, const Version& version) 
    : op(op), version(version) {}

optional<VersionConstraint> VersionConstraint::parse(const string& constraint_str) {
    string trimmed = constraint_str;
    trimmed.erase(0, trimmed.find_first_not_of(" \t"));
    trimmed.erase(trimmed.find_last_not_of(" \t") + 1);
    
    if (trimmed.empty()) return nullopt;
    
    ConstraintOp op = ConstraintOp::EQ;
    string version_str = trimmed;
    
    // Parse operator
    if (trimmed.substr(0, 2) == ">=") {
        op = ConstraintOp::GE;
        version_str = trimmed.substr(2);
    } else if (trimmed.substr(0, 2) == "<=") {
        op = ConstraintOp::LE;
        version_str = trimmed.substr(2);
    } else if (trimmed.substr(0, 2) == "!=") {
        op = ConstraintOp::NE;
        version_str = trimmed.substr(2);
    } else if (trimmed[0] == '>') {
        op = ConstraintOp::GT;
        version_str = trimmed.substr(1);
    } else if (trimmed[0] == '<') {
        op = ConstraintOp::LT;
        version_str = trimmed.substr(1);
    } else if (trimmed[0] == '~') {
        op = ConstraintOp::TILDE;
        version_str = trimmed.substr(1);
    } else if (trimmed[0] == '^') {
        op = ConstraintOp::CARET;
        version_str = trimmed.substr(1);
    } else if (trimmed.substr(0, 2) == "==") {
        op = ConstraintOp::EQ;
        version_str = trimmed.substr(2);
    }
    
    // Remove whitespace
    version_str.erase(0, version_str.find_first_not_of(" \t"));
    version_str.erase(version_str.find_last_not_of(" \t") + 1);
    
    try {
        Version version(version_str);
        return VersionConstraint(op, version);
    } catch (...) {
        return nullopt;
    }
}

vector<VersionConstraint> VersionConstraint::parseMultiple(const string& constraints_str) {
    vector<VersionConstraint> constraints;
    stringstream ss(constraints_str);
    string constraint;
    
    while (getline(ss, constraint, ',')) {
        auto parsed = parse(constraint);
        if (parsed.has_value()) {
            constraints.push_back(parsed.value());
        }
    }
    
    return constraints;
}

bool VersionConstraint::satisfies(const Version& v) const {
    switch (op) {
        case ConstraintOp::EQ:
            return v == version;
        case ConstraintOp::NE:
            return v != version;
        case ConstraintOp::LT:
            return v < version;
        case ConstraintOp::LE:
            return v <= version;
        case ConstraintOp::GT:
            return v > version;
        case ConstraintOp::GE:
            return v >= version;
        case ConstraintOp::TILDE:
            return satisfiesTilde(v);
        case ConstraintOp::CARET:
            return satisfiesCaret(v);
        default:
            return false;
    }
}

bool VersionConstraint::satisfiesTilde(const Version& v) const {
    // ~1.2.3 means >=1.2.3 and <1.3.0
    // ~1.2 means >=1.2.0 and <1.3.0
    // ~1 means >=1.0.0 and <2.0.0
    if (v.getMajor() != version.getMajor()) {
        return false;
    }
    if (v.getMinor() < version.getMinor()) {
        return false;
    }
    if (v.getMinor() > version.getMinor()) {
        return false; // Must be < 1.3.0
    }
    // Same minor version, check patch
    return v >= version;
}

bool VersionConstraint::satisfiesCaret(const Version& v) const {
    // ^1.2.3 means >=1.2.3 and <2.0.0
    // ^0.2.3 means >=0.2.3 and <0.3.0
    // ^0.0.3 means >=0.0.3 and <0.0.4
    if (!(v >= version)) {
        return false;
    }
    
    if (version.getMajor() == 0) {
        if (version.getMinor() == 0) {
            // ^0.0.3 means >=0.0.3 and <0.0.4
            return v.getMajor() == 0 && v.getMinor() == 0 && v.getPatch() < version.getPatch() + 1;
        }
        // ^0.2.3 means >=0.2.3 and <0.3.0
        return v.getMajor() == 0 && v.getMinor() < version.getMinor() + 1;
    }
    
    // ^1.2.3 means >=1.2.3 and <2.0.0
    return v.getMajor() < version.getMajor() + 1;
}

string VersionConstraint::toString() const {
    string op_str;
    switch (op) {
        case ConstraintOp::EQ: op_str = "=="; break;
        case ConstraintOp::NE: op_str = "!="; break;
        case ConstraintOp::LT: op_str = "<"; break;
        case ConstraintOp::LE: op_str = "<="; break;
        case ConstraintOp::GT: op_str = ">"; break;
        case ConstraintOp::GE: op_str = ">="; break;
        case ConstraintOp::TILDE: op_str = "~"; break;
        case ConstraintOp::CARET: op_str = "^"; break;
    }
    return op_str + version.toString();
}

