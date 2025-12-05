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
    cout << "  " << Color::GREEN << "install" << Color::RESET << "  <packages...>  Install packages and dependencies" << endl;
    cout << "  " << Color::GREEN << "update" << Color::RESET << "   <packages...>  Update packages to latest versions" << endl;
    cout << "  " << Color::GREEN << "remove" << Color::RESET << "   <packages...>  Remove installed packages" << endl;
    cout << "  " << Color::GREEN << "list" << Color::RESET << "                    List all installed packages" << endl;
    cout << "  " << Color::GREEN << "resolve" << Color::RESET << "  <packages...>  Show resolution plan (dry run)" << endl;
    cout << "  " << Color::GREEN << "tree" << Color::RESET << "     <packages...>  Show dependency tree" << endl;
    cout << "  " << Color::GREEN << "lock" << Color::RESET << "     <packages...>  Generate lock file without installing" << endl;
    cout << "  " << Color::GREEN << "search" << Color::RESET << "   <query>        Search for packages" << endl;
    cout << "  " << Color::GREEN << "info" << Color::RESET << "     <package>      Show package information" << endl;
    cout << "  " << Color::GREEN << "venv" << Color::RESET << "     [action]       Manage virtual environment" << endl;
    cout << endl;
    
    cout << Color::BOLD << "Examples:" << Color::RESET << endl;
    cout << "  " << Color::DIM << "$" << Color::RESET << " dpm install numpy pandas matplotlib" << endl;
    cout << "  " << Color::DIM << "$" << Color::RESET << " dpm install express lodash  " << Color::DIM << "# npm packages" << Color::RESET << endl;
    cout << "  " << Color::DIM << "$" << Color::RESET << " dpm resolve flask django    " << Color::DIM << "# dry run" << Color::RESET << endl;
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
    
    string command = argv[1];
    vector<string> packages;
    
    for (int i = 2; i < argc; i++) {
        packages.push_back(argv[i]);
    }
    
    // Handle special flags
    if (command == "--help" || command == "-h") {
        printUsage(argv[0]);
        return 0;
    }
    
    if (command == "--version" || command == "-v") {
        printVersion();
        return 0;
    }
    
    CommandHandler handler;
    
    if (command == "install" || command == "i") {
        return handler.handleInstall(packages);
    } else if (command == "update" || command == "u") {
        return handler.handleUpdate(packages);
    } else if (command == "remove" || command == "rm" || command == "uninstall") {
        return handler.handleRemove(packages);
    } else if (command == "list" || command == "ls") {
        return handler.handleList();
    } else if (command == "resolve" || command == "r") {
        return handler.handleResolve(packages);
    } else if (command == "tree" || command == "t") {
        return handler.handleTree(packages);
    } else if (command == "lock") {
        return handler.handleLock(packages);
    } else if (command == "search" || command == "s") {
        if (packages.empty()) {
            Output::error("No search query specified");
            return 1;
        }
        return handler.handleSearch(packages[0]);
    } else if (command == "info") {
        if (packages.empty()) {
            Output::error("No package specified");
            return 1;
        }
        return handler.handleInfo(packages[0]);
    } else if (command == "venv") {
        return handler.handleVenv(packages);
    } else {
        Output::error("Unknown command: " + command);
        cout << endl;
        cout << "Run " << Color::CYAN << "dpm --help" << Color::RESET 
             << " for usage information." << endl;
        return 1;
    }
}
