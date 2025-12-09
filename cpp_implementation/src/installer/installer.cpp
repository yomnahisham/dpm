#include "installer.hpp"
#include "../core/logger.hpp"
#include <cstdlib>
#include <sstream>
#include <cstdio>
#include <cstring>
#include <array>
#include <memory>

using namespace std;

static bool isInVirtualEnvironment() {
    const char* venv = getenv("VIRTUAL_ENV");
    return venv != nullptr && strlen(venv) > 0;
}

Installer::Installer() {}

bool Installer::install(const InstallationPlan& plan) {
    status_message = "Installing " + to_string(plan.size()) + " packages...\n";
    
    auto packages = plan.getInstallationOrder();
    
    for (const auto& package : packages) {
        if (!installPackage(package)) {
            status_message += "Failed to install: " + package.getName() + "\n";
            return false;
        }
        status_message += "Installed: " + package.getName() + " " + package.getVersion() + "\n";
    }
    
    status_message += "Installation complete!\n";
    return true;
}

bool Installer::installPackage(const Package& package) {
    string language = package.getLanguage();
    
    LOG_DEBUG("Installing package: " + package.getName() + " " + package.getVersion() + " (" + language + ")");
    
    if (language == "python") {
        return installPythonPackage(package);
    } else if (language == "javascript") {
        return installJavaScriptPackage(package);
    } else if (language == "system") {
        return installSystemPackage(package);
    } else if (language == "local") {
        // Local packages don't need installation
        LOG_INFO("Local package " + package.getName() + " registered");
        return true;
    }
    
    status_message = "Unknown language: " + language;
    LOG_ERROR("Unknown language: " + language);
    return false;
}

bool Installer::uninstallPackage(const Package& package) {
    string language = package.getLanguage();
    
    LOG_DEBUG("Uninstalling package: " + package.getName() + " (" + language + ")");
    
    if (language == "python") {
        return uninstallPythonPackage(package);
    } else if (language == "javascript") {
        return uninstallJavaScriptPackage(package);
    } else if (language == "system") {
        return uninstallSystemPackage(package);
    } else if (language == "local") {
        // Local packages just need to be removed from state
        return true;
    }
    
    LOG_ERROR("Unknown language for uninstall: " + language);
    return false;
}

string Installer::detectPackageManager() const {
    // Check which package manager is available
    array<string, 2> commands = {"apt-get", "yum"};
    
    for (const auto& cmd : commands) {
        string test_cmd = "which " + cmd + " > /dev/null 2>&1";
        if (system(test_cmd.c_str()) == 0) {
            return cmd;
        }
    }
    
    return "unknown";
}

bool Installer::installPythonPackage(const Package& package) {
    ostringstream cmd;
    // Use pip3 with --user and --break-system-packages for modern Python (PEP 668)
    // But only use --user when NOT in a virtual environment
    cmd << "pip3 install";
    if (!isInVirtualEnvironment()) {
        cmd << " --user";
    }
    cmd << " --break-system-packages --quiet " << package.getName();
    if (!package.getVersion().empty()) {
        cmd << "==" << package.getVersion();
    }
    cmd << " 2>&1";
    
    LOG_DEBUG("Running: " + cmd.str());
    
    int result = system(cmd.str().c_str());
    if (result != 0) {
        LOG_ERROR("pip install failed for " + package.getName());
    }
    return result == 0;
}

bool Installer::uninstallPythonPackage(const Package& package) {
    ostringstream cmd;
    cmd << "pip3 uninstall -y --break-system-packages " << package.getName() << " 2>&1";
    
    LOG_DEBUG("Running: " + cmd.str());
    
    int result = system(cmd.str().c_str());
    return result == 0;
}

bool Installer::installJavaScriptPackage(const Package& package) {
    ostringstream cmd;
    cmd << "npm install --silent " << package.getName();
    if (!package.getVersion().empty()) {
        cmd << "@" << package.getVersion();
    }
    cmd << " 2>&1";
    
    LOG_DEBUG("Running: " + cmd.str());
    
    int result = system(cmd.str().c_str());
    if (result != 0) {
        LOG_ERROR("npm install failed for " + package.getName());
    }
    return result == 0;
}

bool Installer::uninstallJavaScriptPackage(const Package& package) {
    ostringstream cmd;
    cmd << "npm uninstall --silent " << package.getName() << " 2>&1";
    
    LOG_DEBUG("Running: " + cmd.str());
    
    int result = system(cmd.str().c_str());
    return result == 0;
}

bool Installer::installSystemPackage(const Package& package) {
    string pm = detectPackageManager();
    
    ostringstream cmd;
    if (pm == "apt-get") {
        cmd << "sudo apt-get install -y -qq " << package.getName() << " 2>&1";
    } else if (pm == "yum") {
        cmd << "sudo yum install -y -q " << package.getName() << " 2>&1";
    } else {
        LOG_ERROR("No supported system package manager found");
        return false;
    }
    
    LOG_DEBUG("Running: " + cmd.str());
    
    int result = system(cmd.str().c_str());
    return result == 0;
}

bool Installer::uninstallSystemPackage(const Package& package) {
    string pm = detectPackageManager();
    
    ostringstream cmd;
    if (pm == "apt-get") {
        cmd << "sudo apt-get remove -y -qq " << package.getName() << " 2>&1";
    } else if (pm == "yum") {
        cmd << "sudo yum remove -y -q " << package.getName() << " 2>&1";
    } else {
        LOG_ERROR("No supported system package manager found");
        return false;
    }
    
    LOG_DEBUG("Running: " + cmd.str());
    
    int result = system(cmd.str().c_str());
    return result == 0;
}
