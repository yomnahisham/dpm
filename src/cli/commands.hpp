#pragma once

#include "../resolver/resolver.hpp"
#include "../installer/installer.hpp"
#include "../installer/state.hpp"
#include "../installer/lockfile.hpp"
#include "../installer/venv.hpp"
#include "../sources/source.hpp"
#include <string>
#include <vector>
#include <memory>
#include <map>
#include <set>

using namespace std;

// handles all the cli commands
class CommandHandler {
public:
    CommandHandler();
    
    // set up package sources (pypi, npm, etc)
    void initializeSources();
    
    // dpm install <packages>
    int handleInstall(const vector<string>& packages);
    
    // dpm update <packages>
    int handleUpdate(const vector<string>& packages);
    
    // dpm remove <packages>
    int handleRemove(const vector<string>& packages);
    
    // dpm list - shows installed packages
    int handleList();
    
    // dpm resolve - dry run, shows what would be installed
    int handleResolve(const vector<string>& packages);
    
    // dpm tree - shows dependency tree
    int handleTree(const vector<string>& packages);
    
    // dpm lock - creates lock file without installing
    int handleLock(const vector<string>& packages);
    
    // dpm search <query>
    int handleSearch(const string& query);
    
    // dpm info <package> - shows package details
    int handleInfo(const string& package_name);
    
    // dpm venv - create/manage virtual environment
    int handleVenv(const vector<string>& args);
    
private:
    vector<shared_ptr<Source>> sources;
    shared_ptr<DependencyResolver> resolver;
    shared_ptr<Installer> installer;
    shared_ptr<PackageState> state;
    shared_ptr<LockFile> lockfile;
    shared_ptr<VirtualEnv> venv;
    
    // creates installation plan from resolved versions
    InstallationPlan buildPlan(const ResolutionResult& result);
    
    // builds map of package -> dependencies for lock file
    map<string, vector<string>> buildDependencyMap(const ResolutionResult& result);
    
    // builds map of package -> (language, source)
    map<string, pair<string, string>> buildPackageInfo(const ResolutionResult& result);
    
    // recursively prints dependency tree with nice formatting
    void printTree(const string& pkg,
                   const map<string, string>& versions,
                   const map<string, vector<string>>& dep_map,
                   const string& prefix,
                   bool is_last,
                   set<string> visited);
};
