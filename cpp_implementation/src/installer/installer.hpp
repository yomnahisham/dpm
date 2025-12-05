#pragma once

#include "plan.hpp"
#include "../core/package.hpp"
#include <string>
#include <vector>

using namespace std;

// actually installs packages by calling pip/npm/apt
class Installer {
public:
    Installer();
    
    // install everything in the plan
    bool install(const InstallationPlan& plan);
    
    // install one package
    bool installPackage(const Package& package);
    
    // remove one package
    bool uninstallPackage(const Package& package);
    
    string getStatusMessage() const { return status_message; }
    
private:
    string status_message;
    
    // python packages via pip
    bool installPythonPackage(const Package& package);
    bool uninstallPythonPackage(const Package& package);
    
    // js packages via npm
    bool installJavaScriptPackage(const Package& package);
    bool uninstallJavaScriptPackage(const Package& package);
    
    // system packages via apt or yum
    bool installSystemPackage(const Package& package);
    bool uninstallSystemPackage(const Package& package);
    
    // figures out if we have apt, yum, brew, etc
    string detectPackageManager() const;
};
