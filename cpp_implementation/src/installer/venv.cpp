#include "venv.hpp"
#include "../core/logger.hpp"
#include <cstdlib>

using namespace std;

#define LOG_INFO(msg) Logger::instance().info(msg)
#define LOG_ERROR(msg) Logger::instance().error(msg)

VirtualEnv::VirtualEnv() : active(false) {
    base_directory = fs::current_path();
}

VirtualEnv::VirtualEnv(const string& base_dir) : active(false) {
    base_directory = fs::path(base_dir);
}

void VirtualEnv::setPath(const string& name) {
    env_path = base_directory / name;
}

bool VirtualEnv::create(const string& name) {
    env_path = base_directory / name;
    
    if (fs::exists(env_path)) {
        LOG_INFO("virtual environment already exists: " + env_path.string());
        return true;
    }
    
    LOG_INFO("creating virtual environment: " + env_path.string());
    
    // create python venv
    if (!createPythonVenv()) {
        return false;
    }
    
    // create node_modules
    if (!createNodeModules()) {
        return false;
    }
    
    return true;
}

bool VirtualEnv::createPythonVenv() {
    // try python3 -m venv
    string cmd = "python3 -m venv " + env_path.string() + " 2>/dev/null";
    int result = system(cmd.c_str());
    
    if (result != 0) {
        // try python
        cmd = "python -m venv " + env_path.string() + " 2>/dev/null";
        result = system(cmd.c_str());
    }
    
    if (result != 0) {
        LOG_ERROR("failed to create python venv - is python installed?");
        return false;
    }
    
    return true;
}

bool VirtualEnv::createNodeModules() {
    fs::path node_modules = env_path / "node_modules";
    
    try {
        fs::create_directories(node_modules);
        return true;
    } catch (const fs::filesystem_error& e) {
        LOG_ERROR("failed to create node_modules: " + string(e.what()));
        return false;
    }
}

bool VirtualEnv::activate() {
    if (!exists()) {
        LOG_ERROR("cannot activate - venv does not exist");
        return false;
    }
    
    if (active) {
        return true;  // already active
    }
    
    // save original environment
    char* path = getenv("PATH");
    char* venv = getenv("VIRTUAL_ENV");
    original_path = path ? path : "";
    original_virtual_env = venv ? venv : "";
    
    // set new paths
    string venv_bin = (env_path / "bin").string();
    string new_path = venv_bin + ":" + original_path;
    
    setenv("PATH", new_path.c_str(), 1);
    setenv("VIRTUAL_ENV", env_path.string().c_str(), 1);
    
    active = true;
    LOG_INFO("activated virtual environment: " + env_path.string());
    
    return true;
}

void VirtualEnv::deactivate() {
    if (!active) {
        return;
    }
    
    // restore original environment
    if (original_path.empty()) {
        unsetenv("PATH");
    } else {
        setenv("PATH", original_path.c_str(), 1);
    }
    
    if (original_virtual_env.empty()) {
        unsetenv("VIRTUAL_ENV");
    } else {
        setenv("VIRTUAL_ENV", original_virtual_env.c_str(), 1);
    }
    
    active = false;
    LOG_INFO("deactivated virtual environment");
}

bool VirtualEnv::exists() const {
    return fs::exists(env_path) && fs::is_directory(env_path);
}

string VirtualEnv::getPythonPath() const {
    fs::path python = env_path / "bin" / "python";
    if (fs::exists(python)) {
        return python.string();
    }
    // windows
    python = env_path / "Scripts" / "python.exe";
    if (fs::exists(python)) {
        return python.string();
    }
    return "python3";  // fallback
}

string VirtualEnv::getPipPath() const {
    fs::path pip = env_path / "bin" / "pip";
    if (fs::exists(pip)) {
        return pip.string();
    }
    // windows
    pip = env_path / "Scripts" / "pip.exe";
    if (fs::exists(pip)) {
        return pip.string();
    }
    return "pip3";  // fallback
}

string VirtualEnv::getNpmPath() const {
    return "npm";  // use system npm but install to local node_modules
}

string VirtualEnv::getNodeModulesPath() const {
    return (env_path / "node_modules").string();
}

