#include "package.hpp"
#include <sstream>

using namespace std;

Package::Package() {}

Package::Package(const string& name, const string& version, const string& language)
    : name(name), version(version), language(language) {}

Version Package::getVersionObj() const {
    try {
        return Version(version);
    } catch (...) {
        return Version("0.0.0");
    }
}

string Package::toString() const {
    ostringstream oss;
    oss << name << " " << version << " (" << language << ")";
    if (!source.empty()) {
        oss << " from " << source;
    }
    return oss.str();
}



