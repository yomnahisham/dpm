#pragma once

#include <string>
#include <filesystem>
#include <optional>

using namespace std;
namespace fs = std::filesystem;

// manages virtual environments for isolated package installation
// supports python venv and node_modules
class VirtualEnv {
public:
    VirtualEnv();
    explicit VirtualEnv(const string& base_dir);
    
    // create a new virtual environment
    bool create(const string& name = ".dpm_env");
    
    // set the env path without creating (for status check)
    void setPath(const string& name = ".dpm_env");
    
    // activate the environment (sets paths for subprocess calls)
    bool activate();
    
    // deactivate (restore original paths)
    void deactivate();
    
    // check if env exists
    bool exists() const;
    
    // get path to pip/python in the venv
    string getPythonPath() const;
    string getPipPath() const;
    
    // get path to npm/node in local node_modules
    string getNpmPath() const;
    string getNodeModulesPath() const;
    
    // check if currently activated
    bool isActive() const { return active; }
    
    // get the venv directory
    string getPath() const { return env_path.string(); }
    
private:
    fs::path base_directory;
    fs::path env_path;
    bool active;
    
    // saved original paths for deactivation
    string original_path;
    string original_virtual_env;
    
    // create python venv
    bool createPythonVenv();
    
    // create node_modules directory
    bool createNodeModules();
};


