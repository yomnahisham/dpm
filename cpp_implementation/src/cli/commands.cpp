#include "commands.hpp"
#include "../network/cache.hpp"
#include "../sources/pypi.hpp"
#include "../sources/npm.hpp"
#include "../sources/system.hpp"
#include "../sources/local.hpp"
#include "../installer/state.hpp"
#include "../installer/lockfile.hpp"
#include "../installer/venv.hpp"
#include "../core/logger.hpp"
#include "../core/progress.hpp"
#include <iostream>
#include <chrono>
#include <map>
#include <set>
#include <algorithm>
#include <filesystem>

namespace fs = std::filesystem;

using namespace std;

CommandHandler::CommandHandler() {
    resolver = make_shared<DependencyResolver>();
    installer = make_shared<Installer>();
    state = make_shared<PackageState>();
    state->initialize();
    lockfile = make_shared<LockFile>(fs::current_path().string());
    venv = make_shared<VirtualEnv>(fs::current_path().string());
    initializeSources();
}

void CommandHandler::initializeSources() {
    // Initialize cache
    auto cache = make_shared<Cache>();
    cache->initialize();
    
    // Add sources
    sources.push_back(make_shared<PyPISource>(cache));
    sources.push_back(make_shared<NpmSource>(cache));
    sources.push_back(make_shared<SystemSource>());
    sources.push_back(make_shared<LocalSource>());
    
    LOG_DEBUG("Initialized " + to_string(sources.size()) + " package sources");
}

InstallationPlan CommandHandler::buildPlan(const ResolutionResult& result) {
    InstallationPlan plan;
    
    // Fetch packages for resolved versions
    for (const auto& pair : result.selected_versions) {
        string package_name = pair.first;
        string version = pair.second;
        
        // Find source
        for (const auto& source : sources) {
            if (source->packageExists(package_name)) {
                auto package_opt = source->fetchPackage(package_name, version);
                if (package_opt.has_value()) {
                    plan.addPackage(package_opt.value());
                    break;
                }
            }
        }
    }
    
    return plan;
}

int CommandHandler::handleInstall(const vector<string>& packages) {
    auto start_time = chrono::steady_clock::now();
    
    Output::header("DPM Install");
    
    ResolutionResult result;
    bool from_lockfile = false;
    
    // If no packages specified, try to install from lock file
    if (packages.empty()) {
        if (lockfile->exists() && lockfile->load()) {
            Output::info("Installing from lock file: " + lockfile->getPath());
            result.success = true;
            result.selected_versions = lockfile->getLockedVersions();
            from_lockfile = true;
        } else {
            Output::error("No packages specified and no lock file found");
            Output::footer();
            return 1;
        }
    } else {
        // Show what we're installing
        Output::section("Requested packages");
        for (const auto& pkg : packages) {
            cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " " << pkg << endl;
        }
        
        // Check if lock file exists and matches
        if (lockfile->exists() && lockfile->load()) {
            auto locked = lockfile->getLockedVersions();
            bool all_locked = true;
            for (const auto& pkg : packages) {
                if (locked.find(pkg) == locked.end()) {
                    all_locked = false;
                    break;
                }
            }
            if (all_locked) {
                Output::info("Using versions from lock file");
                result.success = true;
                result.selected_versions = locked;
                from_lockfile = true;
            }
        }
        
        if (!from_lockfile) {
            // Resolve dependencies
            Output::section("Resolving dependencies");
            Spinner spinner("Analyzing dependency tree...");
            spinner.start();
            
            LOG_INFO("Resolving dependencies for " + to_string(packages.size()) + " packages");
            
            result = resolver->resolve(packages, sources);
            
            if (!result.success) {
                spinner.stop(false);
                Output::error("Failed to resolve dependencies: " + result.error_message);
                LOG_ERROR("Failed to resolve dependencies: " + result.error_message);
                Output::footer();
                return 1;
            }
            
            spinner.stop(true);
        }
    }
    
    Output::info("Resolved " + to_string(result.selected_versions.size()) + " packages" +
                (result.used_backtracking ? " (used backtracking)" : "") +
                (from_lockfile ? " (from lock file)" : ""));
    
    LOG_INFO("Resolved " + to_string(result.selected_versions.size()) + " packages");
    
    InstallationPlan plan = buildPlan(result);
    auto ordered = plan.getInstallationOrder();
    
    // Show installation plan
    Output::section("Installation plan");
    for (const auto& pkg : ordered) {
        Output::package(pkg.getName(), pkg.getVersion(), 
                       Color::DIM + "(" + pkg.getLanguage() + ")" + Color::RESET);
    }
    
    // Install packages with progress bar
    Output::section("Installing packages");
    
    ProgressBar progress(ordered.size(), "Installing");
    int installed_count = 0;
    bool success = true;
    
    for (size_t i = 0; i < ordered.size(); i++) {
        const auto& pkg = ordered[i];
        progress.setPrefix("Installing " + pkg.getName());
        progress.update(i);
        
        LOG_INFO("Installing " + pkg.getName() + " " + pkg.getVersion());
        
        if (installer->installPackage(pkg)) {
            state->addPackage(pkg);
            installed_count++;
        } else {
            LOG_ERROR("Failed to install " + pkg.getName());
            success = false;
            progress.finish();
            Output::packageFailed(pkg.getName());
            break;
        }
    }
    
    if (success) {
        progress.finish();
        
        // Update lock file if we resolved (not from lock file)
        if (!from_lockfile && !packages.empty()) {
            auto dep_map = buildDependencyMap(result);
            auto pkg_info = buildPackageInfo(result);
            lockfile->setFromResolution(result.selected_versions, dep_map, pkg_info);
            if (lockfile->save()) {
                Output::info("Updated lock file: " + lockfile->getPath());
            }
        }
    }
    
    // Show summary
    auto end_time = chrono::steady_clock::now();
    float elapsed = chrono::duration<float>(end_time - start_time).count();
    
    if (success) {
        Output::stats(result.selected_versions.size(), installed_count, elapsed);
        Output::success("Installation complete!");
        LOG_INFO("Installation complete");
    } else {
        Output::error("Installation failed!");
    }
    
    Output::footer();
    
    return success ? 0 : 1;
}

int CommandHandler::handleUpdate(const vector<string>& packages) {
    Output::header("DPM Update");
    
    if (packages.empty()) {
        // Update all installed packages
        auto installed = state->getInstalledPackages();
        if (installed.empty()) {
            Output::info("No packages installed to update.");
            Output::footer();
            return 0;
        }
        
        vector<string> pkg_names;
        for (const auto& pkg : installed) {
            pkg_names.push_back(pkg.getName());
        }
        
        Output::info("Updating " + to_string(pkg_names.size()) + " installed packages...");
        Output::footer();
        return handleInstall(pkg_names);
    }
    
    // Update specific packages
    Output::footer();
    return handleInstall(packages);
}

int CommandHandler::handleRemove(const vector<string>& packages) {
    auto start_time = chrono::steady_clock::now();
    
    if (packages.empty()) {
        Output::error("No packages specified");
        return 1;
    }
    
    Output::header("DPM Remove");
    
    int removed_count = 0;
    bool success = true;
    
    ProgressBar progress(packages.size(), "Removing");
    
    for (size_t i = 0; i < packages.size(); i++) {
        const auto& pkg_name = packages[i];
        progress.setPrefix("Removing " + pkg_name);
        progress.update(i);
        
        if (!state->isInstalled(pkg_name)) {
            Output::warning("Package not installed: " + pkg_name);
            continue;
        }
        
        auto version = state->getInstalledVersion(pkg_name);
        
        // Create a package object for uninstallation
        Package pkg;
        pkg.setName(pkg_name);
        if (version.has_value()) {
            pkg.setVersion(version.value());
        }
        
        // Try to determine language from state
        auto installed = state->getInstalledPackages();
        for (const auto& p : installed) {
            if (p.getName() == pkg_name) {
                pkg.setLanguage(p.getLanguage());
                break;
            }
        }
        
        if (installer->uninstallPackage(pkg)) {
            state->removePackage(pkg_name);
            removed_count++;
            LOG_INFO("Removed " + pkg_name);
        } else {
            LOG_ERROR("Failed to remove " + pkg_name);
            success = false;
        }
    }
    
    progress.finish();
    
    auto end_time = chrono::steady_clock::now();
    float elapsed = chrono::duration<float>(end_time - start_time).count();
    
    cout << endl;
    cout << Color::YELLOW << Symbol::TRASH << " " << removed_count << Color::RESET 
         << " packages removed in " << Color::CYAN << fixed << setprecision(1) 
         << elapsed << "s" << Color::RESET << endl;
    
    if (success) {
        Output::success("Removal complete!");
    } else {
        Output::error("Some packages failed to remove");
    }
    
    Output::footer();
    
    return success ? 0 : 1;
}

int CommandHandler::handleList() {
    auto installed = state->getInstalledPackages();
    
    Output::header("Installed Packages");
    
    if (installed.empty()) {
        Output::info("No packages installed.");
        Output::footer();
        return 0;
    }
    
    // Build table data
    vector<vector<string>> rows;
    for (const auto& pkg : installed) {
        rows.push_back({
            pkg.getName(),
            pkg.getVersion(),
            pkg.getLanguage(),
            pkg.getSource()
        });
    }
    
    Output::table(rows, {"Package", "Version", "Language", "Source"});
    
    cout << endl;
    cout << Color::DIM << "Total: " << Color::RESET << Color::BOLD 
         << installed.size() << Color::RESET << " packages" << endl;
    
    Output::footer();
    
    return 0;
}

int CommandHandler::handleResolve(const vector<string>& packages) {
    auto start_time = chrono::steady_clock::now();
    
    if (packages.empty()) {
        Output::error("No packages specified");
        return 1;
    }
    
    Output::header("DPM Resolve (Dry Run)");
    
    // Show what we're resolving
    Output::section("Requested packages");
    for (const auto& pkg : packages) {
        cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " " << pkg << endl;
    }
    
    // Resolve dependencies
    Output::section("Resolving dependencies");
    Spinner spinner("Analyzing dependency tree...");
    spinner.start();
    
    ResolutionResult result = resolver->resolve(packages, sources);
    
    auto end_time = chrono::steady_clock::now();
    float elapsed = chrono::duration<float>(end_time - start_time).count();
    
    if (!result.success) {
        spinner.stop(false);
        Output::error("Failed to resolve dependencies: " + result.error_message);
        Output::footer();
        return 1;
    }
    
    spinner.stop(true);
    
    // Show results
    Output::section("Resolution result");
    Output::info("Algorithm: " + string(result.used_backtracking ? "Backtracking" : "Greedy"));
    Output::info("Packages resolved: " + to_string(result.selected_versions.size()));
    Output::info("Time: " + to_string(elapsed).substr(0, 4) + "s");
    
    // Show selected versions
    Output::section("Selected versions");
    
    vector<vector<string>> rows;
    for (const auto& pair : result.selected_versions) {
        rows.push_back({pair.first, pair.second});
    }
    Output::table(rows, {"Package", "Version"});
    
    // Show installation order
    InstallationPlan plan = buildPlan(result);
    auto ordered = plan.getInstallationOrder();
    
    Output::section("Installation order");
    int order_num = 1;
    for (const auto& pkg : ordered) {
        cout << "  " << Color::DIM << setw(3) << order_num++ << "." << Color::RESET << " ";
        cout << Color::BOLD << pkg.getName() << Color::RESET;
        cout << " " << Color::DIM << pkg.getVersion() << Color::RESET << endl;
    }
    
    Output::footer();
    
    return 0;
}

int CommandHandler::handleTree(const vector<string>& packages) {
    if (packages.empty()) {
        auto installed = state->getInstalledPackages();
        if (installed.empty()) {
            Output::header("Dependency Tree");
            Output::info("No packages installed.");
            Output::footer();
            return 0;
        }
        
        vector<string> pkg_names;
        for (const auto& pkg : installed) {
            pkg_names.push_back(pkg.getName());
        }
        return handleTree(pkg_names);
    }
    
    Output::header("Dependency Tree");
    
    Spinner spinner("Building dependency tree...");
    spinner.start();
    
    ResolutionResult result = resolver->resolve(packages, sources);
    
    if (!result.success) {
        spinner.stop(false);
        Output::error("Failed to resolve: " + result.error_message);
        Output::footer();
        return 1;
    }
    
    spinner.stop(true);
    
    // Use the resolver's graph to get dependency relationships
    map<string, vector<string>> dep_map;
    
    // Build a lowercase lookup map for package names
    map<string, string> name_lookup;  // lowercase -> actual
    for (const auto& pair : result.selected_versions) {
        string lower = pair.first;
        transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
        // Replace - with _ for normalization
        replace(lower.begin(), lower.end(), '-', '_');
        name_lookup[lower] = pair.first;
    }
    
    for (const auto& pair : result.selected_versions) {
        string pkg_name = pair.first;
        string version = pair.second;
        
        for (const auto& source : sources) {
            if (source->packageExists(pkg_name)) {
                auto pkg_opt = source->fetchLatest(pkg_name);  // Use fetchLatest to get deps
                if (pkg_opt.has_value()) {
                    vector<string> deps;
                    for (const auto& dep : pkg_opt->getDependencies()) {
                        string dep_name = dep.getName();
                        string dep_lower = dep_name;
                        transform(dep_lower.begin(), dep_lower.end(), dep_lower.begin(), ::tolower);
                        replace(dep_lower.begin(), dep_lower.end(), '-', '_');
                        
                        // Look up normalized name
                        auto it = name_lookup.find(dep_lower);
                        if (it != name_lookup.end()) {
                            deps.push_back(it->second);
                        }
                    }
                    dep_map[pkg_name] = deps;
                    break;
                }
            }
        }
    }
    
    cout << endl;
    // Only print the requested packages as roots (not their dependencies)
    for (size_t i = 0; i < packages.size(); i++) {
        set<string> visited;
        if (result.selected_versions.count(packages[i]) > 0) {
            printTree(packages[i], result.selected_versions, dep_map, "", true, visited);
            if (i < packages.size() - 1) cout << endl;
        }
    }
    
    cout << endl;
    cout << Color::DIM << "Total: " << Color::RESET << Color::BOLD 
         << result.selected_versions.size() << Color::RESET << " packages" << endl;
    
    Output::footer();
    return 0;
}

void CommandHandler::printTree(const string& pkg, 
                               const map<string, string>& versions,
                               const map<string, vector<string>>& dep_map,
                               const string& prefix,
                               bool is_last,
                               set<string> visited) {
    string version = "";
    auto it = versions.find(pkg);
    if (it != versions.end()) version = it->second;
    
    bool is_circular = visited.count(pkg) > 0;
    
    cout << prefix;
    if (prefix.empty()) {
        cout << Color::BOLD << Color::CYAN << pkg << Color::RESET;
    } else {
        cout << (is_last ? "`-- " : "|-- ");
        cout << Color::BOLD << pkg << Color::RESET;
    }
    
    if (!version.empty()) cout << Color::DIM << " " << version << Color::RESET;
    
    if (is_circular) {
        cout << Color::YELLOW << " (circular)" << Color::RESET << endl;
        return;
    }
    
    cout << endl;
    visited.insert(pkg);
    
    auto dep_it = dep_map.find(pkg);
    if (dep_it == dep_map.end() || dep_it->second.empty()) return;
    
    // Use deps directly - they're already validated
    const vector<string>& resolved_deps = dep_it->second;
    
    for (size_t i = 0; i < resolved_deps.size(); i++) {
        string new_prefix;
        if (prefix.empty()) {
            new_prefix = "    ";  // First level indent
        } else {
            new_prefix = prefix + (is_last ? "    " : "|   ");
        }
        printTree(resolved_deps[i], versions, dep_map, new_prefix, i == resolved_deps.size() - 1, visited);
    }
}

map<string, vector<string>> CommandHandler::buildDependencyMap(const ResolutionResult& result) {
    map<string, vector<string>> dep_map;
    
    map<string, string> name_lookup;
    for (const auto& pair : result.selected_versions) {
        string lower = pair.first;
        transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
        replace(lower.begin(), lower.end(), '-', '_');
        name_lookup[lower] = pair.first;
    }
    
    for (const auto& pair : result.selected_versions) {
        string pkg_name = pair.first;
        
        for (const auto& source : sources) {
            if (source->packageExists(pkg_name)) {
                auto pkg_opt = source->fetchLatest(pkg_name);
                if (pkg_opt.has_value()) {
                    vector<string> deps;
                    for (const auto& dep : pkg_opt->getDependencies()) {
                        string dep_name = dep.getName();
                        string dep_lower = dep_name;
                        transform(dep_lower.begin(), dep_lower.end(), dep_lower.begin(), ::tolower);
                        replace(dep_lower.begin(), dep_lower.end(), '-', '_');
                        
                        auto it = name_lookup.find(dep_lower);
                        if (it != name_lookup.end()) {
                            deps.push_back(it->second);
                        }
                    }
                    dep_map[pkg_name] = deps;
                    break;
                }
            }
        }
    }
    
    return dep_map;
}

map<string, pair<string, string>> CommandHandler::buildPackageInfo(const ResolutionResult& result) {
    map<string, pair<string, string>> info;
    
    for (const auto& pair : result.selected_versions) {
        string pkg_name = pair.first;
        string version = pair.second;
        
        for (const auto& source : sources) {
            if (source->packageExists(pkg_name)) {
                auto pkg_opt = source->fetchPackage(pkg_name, version);
                if (pkg_opt.has_value()) {
                    info[pkg_name] = {pkg_opt->getLanguage(), pkg_opt->getSource()};
                    break;
                }
            }
        }
    }
    
    return info;
}

int CommandHandler::handleLock(const vector<string>& packages) {
    Output::header("DPM Lock");
    
    if (packages.empty()) {
        Output::error("No packages specified");
        Output::footer();
        return 1;
    }
    
    Output::section("Requested packages");
    for (const auto& pkg : packages) {
        cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " " << pkg << endl;
    }
    
    Output::section("Resolving dependencies");
    Spinner spinner("Analyzing dependency tree...");
    spinner.start();
    
    ResolutionResult result = resolver->resolve(packages, sources);
    
    if (!result.success) {
        spinner.stop(false);
        Output::error("Failed to resolve dependencies: " + result.error_message);
        Output::footer();
        return 1;
    }
    
    spinner.stop(true);
    
    Output::info("Resolved " + to_string(result.selected_versions.size()) + " packages");
    
    // Build and save lock file
    auto dep_map = buildDependencyMap(result);
    auto pkg_info = buildPackageInfo(result);
    lockfile->setFromResolution(result.selected_versions, dep_map, pkg_info);
    
    if (lockfile->save()) {
        Output::success("Lock file created: " + lockfile->getPath());
        
        // Show locked packages
        Output::section("Locked packages");
        for (const auto& [name, version] : result.selected_versions) {
            cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " "
                 << Color::BOLD << name << Color::RESET << " " 
                 << Color::DIM << version << Color::RESET << endl;
        }
    } else {
        Output::error("Failed to create lock file");
        Output::footer();
        return 1;
    }
    
    Output::footer();
    return 0;
}

int CommandHandler::handleSearch(const string& query) {
    Output::header("DPM Search: " + query);
    
    Spinner spinner("Searching packages...");
    spinner.start();
    
    vector<tuple<string, string, string>> results;  // name, version, source
    
    for (const auto& source : sources) {
        if (source->packageExists(query)) {
            auto pkg = source->fetchLatest(query);
            if (pkg.has_value()) {
                results.push_back({pkg->getName(), pkg->getVersion(), source->getName()});
            }
        }
    }
    
    spinner.stop(true);
    
    if (results.empty()) {
        Output::info("No packages found matching '" + query + "'");
    } else {
        Output::section("Found packages");
        for (const auto& [name, version, src] : results) {
            cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " "
                 << Color::BOLD << name << Color::RESET << " "
                 << Color::DIM << version << Color::RESET << " "
                 << Color::DIM << "(" << src << ")" << Color::RESET << endl;
        }
    }
    
    Output::footer();
    return results.empty() ? 1 : 0;
}

int CommandHandler::handleInfo(const string& package_name) {
    Output::header("Package Info: " + package_name);
    
    Spinner spinner("Fetching package info...");
    spinner.start();
    
    optional<Package> found_pkg;
    string source_name;
    vector<string> all_versions;
    
    for (const auto& source : sources) {
        if (source->packageExists(package_name)) {
            auto pkg = source->fetchLatest(package_name);
            if (pkg.has_value()) {
                found_pkg = pkg;
                source_name = source->getName();
                all_versions = source->getAvailableVersions(package_name);
                break;
            }
        }
    }
    
    spinner.stop(found_pkg.has_value());
    
    if (!found_pkg.has_value()) {
        Output::error("Package not found: " + package_name);
        Output::footer();
        return 1;
    }
    
    const Package& pkg = found_pkg.value();
    
    Output::section("Package details");
    cout << "  " << Color::BOLD << "Name:     " << Color::RESET << pkg.getName() << endl;
    cout << "  " << Color::BOLD << "Version:  " << Color::RESET << pkg.getVersion() << " (latest)" << endl;
    cout << "  " << Color::BOLD << "Language: " << Color::RESET << pkg.getLanguage() << endl;
    cout << "  " << Color::BOLD << "Source:   " << Color::RESET << source_name << endl;
    
    auto deps = pkg.getDependencies();
    if (!deps.empty()) {
        Output::section("Dependencies (" + to_string(deps.size()) + ")");
        for (const auto& dep : deps) {
            cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " " << dep.getName() << endl;
        }
    }
    
    if (!all_versions.empty()) {
        vector<Version> sorted_versions;
        for (const auto& v : all_versions) {
            try { sorted_versions.push_back(Version(v)); } catch (...) {}
        }
        sort(sorted_versions.begin(), sorted_versions.end());
        reverse(sorted_versions.begin(), sorted_versions.end());
        
        Output::section("Available versions (" + to_string(all_versions.size()) + " total)");
        for (int i = 0; i < min(10, (int)sorted_versions.size()); i++) {
            cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " " << sorted_versions[i].toString();
            if (i == 0) cout << Color::GREEN << " (latest)" << Color::RESET;
            cout << endl;
        }
        if (sorted_versions.size() > 10) {
            cout << "  " << Color::DIM << "... and " << (sorted_versions.size() - 10) << " more" << Color::RESET << endl;
        }
    }
    
    Output::footer();
    return 0;
}

int CommandHandler::handleVenv(const vector<string>& args) {
    string action = args.empty() ? "create" : args[0];
    string env_name = args.size() > 1 ? args[1] : ".dpm_env";
    
    Output::header("DPM Virtual Environment");
    
    if (action == "create") {
        Output::info("Creating virtual environment: " + env_name);
        
        Spinner spinner("Setting up environment...");
        spinner.start();
        
        venv = make_shared<VirtualEnv>(fs::current_path().string());
        bool success = venv->create(env_name);
        
        spinner.stop(success);
        
        if (success) {
            Output::success("Virtual environment created!");
            Output::section("Activation");
            cout << "  To activate:" << endl;
            cout << "  " << Color::CYAN << "source " << env_name << "/bin/activate" << Color::RESET << endl;
            cout << endl;
            cout << "  Or use dpm with --venv flag:" << endl;
            cout << "  " << Color::CYAN << "dpm install --venv requests" << Color::RESET << endl;
        } else {
            Output::error("Failed to create virtual environment");
            Output::footer();
            return 1;
        }
    } else if (action == "activate") {
        if (!venv->exists()) {
            Output::error("No virtual environment found. Run 'dpm venv create' first.");
            Output::footer();
            return 1;
        }
        
        if (venv->activate()) {
            Output::success("Virtual environment activated!");
            Output::info("Python: " + venv->getPythonPath());
            Output::info("Pip: " + venv->getPipPath());
        } else {
            Output::error("Failed to activate virtual environment");
            Output::footer();
            return 1;
        }
    } else if (action == "deactivate") {
        venv->deactivate();
        Output::success("Virtual environment deactivated");
    } else if (action == "status") {
        // check for default env name
        venv = make_shared<VirtualEnv>(fs::current_path().string());
        venv->setPath(env_name);
        
        if (venv->exists()) {
            Output::info("Virtual environment: " + venv->getPath());
            Output::info("Active: " + string(venv->isActive() ? "yes" : "no"));
            Output::info("Python: " + venv->getPythonPath());
            Output::info("Pip: " + venv->getPipPath());
        } else {
            Output::info("No virtual environment found");
        }
    } else {
        Output::error("Unknown action: " + action);
        Output::info("Available actions: create, activate, deactivate, status");
        Output::footer();
        return 1;
    }
    
    Output::footer();
    return 0;
}
