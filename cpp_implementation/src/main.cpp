#include "cli/commands.hpp"
#include "core/progress.hpp"
#include <iostream>
#include <vector>

using namespace std;

void printUsage(const char* program_name) {
    cout << endl;
    cout << Color::BOLD << Color::CYAN;
    cout << "  ____  ____  __  __ " << endl;
    cout << " |  _ \\|  _ \\|  \\/  |" << endl;
    cout << " | | | | |_) | |\\/| |" << endl;
    cout << " | |_| |  __/| |  | |" << endl;
    cout << " |____/|_|   |_|  |_|" << endl;
    cout << Color::RESET << endl;
    cout << Color::DIM << " Dependency Package Manager" << Color::RESET << endl;
    cout << endl;
    
    cout << Color::BOLD << "Usage:" << Color::RESET << " " << program_name << " <command> [packages...]" << endl;
    cout << endl;
    
    cout << Color::BOLD << "Commands:" << Color::RESET << endl;
    cout << "  " << Color::GREEN << "install" << Color::RESET << "   <packages...>  Install packages and dependencies" << endl;
    cout << "  " << Color::GREEN << "update" << Color::RESET << "    <packages...>  Update packages to latest versions" << endl;
    cout << "  " << Color::GREEN << "remove" << Color::RESET << "    <packages...>  Remove installed packages" << endl;
    cout << "  " << Color::GREEN << "list" << Color::RESET << "                     List all installed packages" << endl;
    cout << "  " << Color::GREEN << "resolve" << Color::RESET << "   <packages...>  Show resolution plan (dry run)" << endl;
    cout << "  " << Color::GREEN << "tree" << Color::RESET << "      <packages...>  Show dependency tree" << endl;
    cout << "  " << Color::GREEN << "lock" << Color::RESET << "      <packages...>  Generate lock file without installing" << endl;
    cout << "  " << Color::GREEN << "search" << Color::RESET << "    <query>        Search for packages" << endl;
    cout << "  " << Color::GREEN << "info" << Color::RESET << "      <package>      Show package information" << endl;
    cout << "  " << Color::GREEN << "venv" << Color::RESET << "      [command]      Manage virtual environment" << endl;
    cout << "  " << Color::GREEN << "init" << Color::RESET << "                    Initialize dpm.json manifest file" << endl;
    cout << "  " << Color::GREEN << "clean" << Color::RESET << "                   Remove unused packages" << endl;
    cout << "  " << Color::GREEN << "outdated" << Color::RESET << "                Check for outdated packages" << endl;
    cout << "  " << Color::GREEN << "cache" << Color::RESET << "     [command]      Manage cache (clear, info, list)" << endl;
    cout << "  " << Color::GREEN << "pin" << Color::RESET << "       <pkg>@<version> Pin package to exact version" << endl;
    cout << "  " << Color::GREEN << "unpin" << Color::RESET << "     <pkg>          Unpin package (allow version ranges)" << endl;
    cout << "  " << Color::GREEN << "export" << Color::RESET << "    <format>       Export dependencies (requirements.txt, package.json)" << endl;
    cout << "  " << Color::GREEN << "repo" << Color::RESET << "      [command]      Manage custom repositories" << endl;
    cout << endl;
    
    cout << Color::BOLD << "Options:" << Color::RESET << endl;
    cout << "  " << Color::CYAN << "--verbose, -v" << Color::RESET << "            Verbose output" << endl;
    cout << "  " << Color::CYAN << "--debug, -d" << Color::RESET << "              Debug output (includes verbose)" << endl;
    cout << "  " << Color::CYAN << "--offline" << Color::RESET << "                Offline mode (use cache only)" << endl;
    cout << "  " << Color::CYAN << "--skip-integrity" << Color::RESET << "         Skip integrity verification" << endl;
    cout << "  " << Color::CYAN << "--show-resolution" << Color::RESET << "        Show detailed resolution steps" << endl;
    cout << endl;
    
    cout << Color::BOLD << "Examples:" << Color::RESET << endl;
    cout << "  " << Color::DIM << "$" << Color::RESET << " dpm install numpy pandas matplotlib" << endl;
    cout << "  " << Color::DIM << "$" << Color::RESET << " dpm resolve flask django" << endl;
    cout << "  " << Color::DIM << "$" << Color::RESET << " dpm list" << endl;
    cout << endl;
    
    cout << Color::BOLD << "Supported Sources:" << Color::RESET << endl;
    cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " PyPI (Python)" << endl;
    cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " npm (JavaScript)" << endl;
    cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " System (apt/yum)" << endl;
    cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " Local (JSON files)" << endl;
    cout << endl;
}

void printVersion() {
    cout << Color::BOLD << "DPM" << Color::RESET << " version " 
         << Color::CYAN << "1.0.0" << Color::RESET << endl;
    cout << Color::DIM << "Cross-language dependency package manager" << Color::RESET << endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }
    
    // Parse flags
    bool verbose = false;
    bool debug = false;
    bool offline = false;
    bool skip_integrity = false;
    bool show_resolution = false;
    
    vector<string> args;
    string command;
    
    // Parse arguments, separating flags from command and packages
    for (int i = 1; i < argc; i++) {
        string arg = argv[i];
        if (arg == "--verbose" || arg == "-v") {
            verbose = true;
        } else if (arg == "--debug" || arg == "-d") {
            debug = true;
            verbose = true; // debug implies verbose
        } else if (arg == "--offline") {
            offline = true;
        } else if (arg == "--skip-integrity") {
            skip_integrity = true;
        } else if (arg == "--show-resolution") {
            show_resolution = true;
        } else if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            return 0;
        } else if (arg == "--version" || arg == "-V") {
            printVersion();
            return 0;
        } else if (command.empty() && arg[0] != '-') {
            // First non-flag argument is the command
            command = arg;
        } else if (!command.empty()) {
            // Everything after command is packages/args
            args.push_back(arg);
        }
    }
    
    if (command.empty()) {
        printUsage(argv[0]);
        return 1;
    }
    
    CommandHandler handler(verbose, debug, offline, skip_integrity, show_resolution);
    
    if (command == "install" || command == "i") {
        return handler.handleInstall(args);
    } else if (command == "update" || command == "u") {
        return handler.handleUpdate(args);
    } else if (command == "remove" || command == "rm" || command == "uninstall") {
        return handler.handleRemove(args);
    } else if (command == "list" || command == "ls") {
        return handler.handleList();
    } else if (command == "resolve" || command == "r") {
        return handler.handleResolve(args);
    } else if (command == "tree" || command == "t") {
        return handler.handleTree(args);
    } else if (command == "lock") {
        return handler.handleLock(args);
    } else if (command == "search" || command == "s") {
        if (args.empty()) {
            Output::error("No search query specified");
            return 1;
        }
        return handler.handleSearch(args[0]);
    } else if (command == "info") {
        if (args.empty()) {
            Output::error("No package specified");
            return 1;
        }
        return handler.handleInfo(args[0]);
    } else if (command == "venv") {
        return handler.handleVenv(args);
    } else if (command == "init") {
        return handler.handleInit(args);
    } else if (command == "clean") {
        return handler.handleClean(args);
    } else if (command == "outdated") {
        return handler.handleOutdated(args);
    } else if (command == "cache") {
        return handler.handleCache(args);
    } else if (command == "pin") {
        return handler.handlePin(args);
    } else if (command == "unpin") {
        return handler.handleUnpin(args);
    } else if (command == "export") {
        return handler.handleExport(args);
    } else if (command == "repo") {
        return handler.handleRepo(args);
    } else {
        Output::error("Unknown command: " + command);
        cout << endl;
        cout << "Run " << Color::CYAN << "dpm --help" << Color::RESET 
             << " for usage information." << endl;
        return 1;
    }
}
