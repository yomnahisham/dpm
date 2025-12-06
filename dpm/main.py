#!/usr/bin/env python3
"""
main.py - entry point for dpm
"""

import sys
import argparse
from .cli.commands import CommandHandler


def print_usage(program_name: str):
    """print usage information"""
    print()
    print("  ____  ____  __  __ ")
    print(" |  _ \\|  _ \\|  \\/  |")
    print(" | | | | |_) | |\\/| |")
    print(" | |_| |  __/| |  | |")
    print(" |____/|_|   |_|  |_|")
    print()
    print(" Dependency Package Manager")
    print()
    print(f"Usage: {program_name} <command> [packages...]")
    print()
    print("Commands:")
    print("  install   <packages...>  Install packages and dependencies")
    print("  update    <packages...>  Update packages to latest versions")
    print("  remove    <packages...>  Remove installed packages")
    print("  list                     List all installed packages")
    print("  resolve   <packages...>  Show resolution plan (dry run)")
    print("  tree      <packages...>  Show dependency tree")
    print("  lock      <packages...>  Generate lock file without installing")
    print("  search    <query>        Search for packages")
    print("  info      <package>      Show package information")
    print("  venv      [command]      Manage virtual environment")
    print("  init                     Initialize dpm.json manifest file")
    print("  clean                    Remove unused packages")
    print("  outdated                 Check for outdated packages")
    print("  cache                    Manage cache (clear, info, list)")
    print("  pin      <pkg>@<version> Pin package to exact version")
    print("  unpin    <pkg>           Unpin package (allow version ranges)")
    print("  export   <format>        Export dependencies (requirements.txt, package.json)")
    print("  repo     [command]        Manage custom repositories")
    print()
    print("Options:")
    print("  --verbose, -v            Verbose output")
    print("  --debug, -d              Debug output (includes verbose)")
    print("  --offline                Offline mode (use cache only)")
    print("  --skip-integrity         Skip integrity verification")
    print("  --show-resolution        Show detailed resolution steps")
    print()
    print("Examples:")
    print(f"  dpm install numpy pandas matplotlib")
    print(f"  dpm resolve flask django")
    print(f"  dpm list")
    print()


def print_version():
    """print version information"""
    print("DPM version 1.0.0")
    print("Cross-language dependency package manager")


def main():
    """main entry point"""
    parser = argparse.ArgumentParser(prog='dpm', add_help=False)
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--debug', '-d', action='store_true', help='debug output')
    parser.add_argument('--offline', action='store_true', help='offline mode (use cache only)')
    parser.add_argument('--skip-integrity', action='store_true', help='skip integrity verification')
    parser.add_argument('--show-resolution', action='store_true', help='show detailed resolution steps')
    
    # parse known args to extract flags, rest goes to command
    args, remaining = parser.parse_known_args()
    
    if len(remaining) < 1:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 1
    
    command = remaining[0]
    packages = remaining[1:] if len(remaining) > 1 else []
    
    # handle special flags
    if command in ["--help", "-h"]:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 0
    
    if command in ["--version", "-V"]:
        print_version()
        return 0
    
    handler = CommandHandler(
        verbose=args.verbose, 
        debug=args.debug, 
        offline=args.offline, 
        skip_integrity=args.skip_integrity,
        show_resolution=args.show_resolution
    )
    
    if command in ["install", "i"]:
        return handler.handle_install(packages)
    elif command in ["update", "u"]:
        return handler.handle_update(packages)
    elif command in ["remove", "rm", "uninstall"]:
        return handler.handle_remove(packages)
    elif command in ["list", "ls"]:
        return handler.handle_list()
    elif command in ["resolve", "r"]:
        return handler.handle_resolve(packages)
    elif command in ["tree", "t"]:
        return handler.handle_tree(packages)
    elif command == "lock":
        return handler.handle_lock(packages)
    elif command in ["search", "s"]:
        if not packages:
            print("Error: No search query specified")
            return 1
        return handler.handle_search(packages[0])
    elif command == "info":
        if not packages:
            print("Error: No package specified")
            return 1
        return handler.handle_info(packages[0])
    elif command == "venv":
        return handler.handle_venv(packages)
    elif command == "init":
        return handler.handle_init(packages)
    elif command == "clean":
        return handler.handle_clean(packages)
    elif command == "outdated":
        return handler.handle_outdated(packages)
    elif command == "cache":
        return handler.handle_cache(packages)
    elif command == "pin":
        return handler.handle_pin(packages)
    elif command == "unpin":
        return handler.handle_unpin(packages)
    elif command == "export":
        return handler.handle_export(packages)
    elif command == "repo":
        return handler.handle_repo(packages)
    else:
        print(f"Error: Unknown command: {command}")
        print()
        print(f"Run {sys.argv[0] if sys.argv else 'dpm'} --help for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


main.py - entry point for dpm
"""

import sys
import argparse
from .cli.commands import CommandHandler


def print_usage(program_name: str):
    """print usage information"""
    print()
    print("  ____  ____  __  __ ")
    print(" |  _ \\|  _ \\|  \\/  |")
    print(" | | | | |_) | |\\/| |")
    print(" | |_| |  __/| |  | |")
    print(" |____/|_|   |_|  |_|")
    print()
    print(" Dependency Package Manager")
    print()
    print(f"Usage: {program_name} <command> [packages...]")
    print()
    print("Commands:")
    print("  install   <packages...>  Install packages and dependencies")
    print("  update    <packages...>  Update packages to latest versions")
    print("  remove    <packages...>  Remove installed packages")
    print("  list                     List all installed packages")
    print("  resolve   <packages...>  Show resolution plan (dry run)")
    print("  tree      <packages...>  Show dependency tree")
    print("  lock      <packages...>  Generate lock file without installing")
    print("  search    <query>        Search for packages")
    print("  info      <package>      Show package information")
    print("  venv      [command]      Manage virtual environment")
    print("  init                     Initialize dpm.json manifest file")
    print("  clean                    Remove unused packages")
    print("  outdated                 Check for outdated packages")
    print("  cache                    Manage cache (clear, info, list)")
    print("  pin      <pkg>@<version> Pin package to exact version")
    print("  unpin    <pkg>           Unpin package (allow version ranges)")
    print("  export   <format>        Export dependencies (requirements.txt, package.json)")
    print("  repo     [command]        Manage custom repositories")
    print()
    print("Options:")
    print("  --verbose, -v            Verbose output")
    print("  --debug, -d              Debug output (includes verbose)")
    print("  --offline                Offline mode (use cache only)")
    print("  --skip-integrity         Skip integrity verification")
    print("  --show-resolution        Show detailed resolution steps")
    print()
    print("Examples:")
    print(f"  dpm install numpy pandas matplotlib")
    print(f"  dpm resolve flask django")
    print(f"  dpm list")
    print()


def print_version():
    """print version information"""
    print("DPM version 1.0.0")
    print("Cross-language dependency package manager")


def main():
    """main entry point"""
    parser = argparse.ArgumentParser(prog='dpm', add_help=False)
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--debug', '-d', action='store_true', help='debug output')
    parser.add_argument('--offline', action='store_true', help='offline mode (use cache only)')
    parser.add_argument('--skip-integrity', action='store_true', help='skip integrity verification')
    parser.add_argument('--show-resolution', action='store_true', help='show detailed resolution steps')
    
    # parse known args to extract flags, rest goes to command
    args, remaining = parser.parse_known_args()
    
    if len(remaining) < 1:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 1
    
    command = remaining[0]
    packages = remaining[1:] if len(remaining) > 1 else []
    
    # handle special flags
    if command in ["--help", "-h"]:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 0
    
    if command in ["--version", "-V"]:
        print_version()
        return 0
    
    handler = CommandHandler(
        verbose=args.verbose, 
        debug=args.debug, 
        offline=args.offline, 
        skip_integrity=args.skip_integrity,
        show_resolution=args.show_resolution
    )
    
    if command in ["install", "i"]:
        return handler.handle_install(packages)
    elif command in ["update", "u"]:
        return handler.handle_update(packages)
    elif command in ["remove", "rm", "uninstall"]:
        return handler.handle_remove(packages)
    elif command in ["list", "ls"]:
        return handler.handle_list()
    elif command in ["resolve", "r"]:
        return handler.handle_resolve(packages)
    elif command in ["tree", "t"]:
        return handler.handle_tree(packages)
    elif command == "lock":
        return handler.handle_lock(packages)
    elif command in ["search", "s"]:
        if not packages:
            print("Error: No search query specified")
            return 1
        return handler.handle_search(packages[0])
    elif command == "info":
        if not packages:
            print("Error: No package specified")
            return 1
        return handler.handle_info(packages[0])
    elif command == "venv":
        return handler.handle_venv(packages)
    elif command == "init":
        return handler.handle_init(packages)
    elif command == "clean":
        return handler.handle_clean(packages)
    elif command == "outdated":
        return handler.handle_outdated(packages)
    elif command == "cache":
        return handler.handle_cache(packages)
    elif command == "pin":
        return handler.handle_pin(packages)
    elif command == "unpin":
        return handler.handle_unpin(packages)
    elif command == "export":
        return handler.handle_export(packages)
    elif command == "repo":
        return handler.handle_repo(packages)
    else:
        print(f"Error: Unknown command: {command}")
        print()
        print(f"Run {sys.argv[0] if sys.argv else 'dpm'} --help for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


main.py - entry point for dpm
"""

import sys
import argparse
from .cli.commands import CommandHandler


def print_usage(program_name: str):
    """print usage information"""
    print()
    print("  ____  ____  __  __ ")
    print(" |  _ \\|  _ \\|  \\/  |")
    print(" | | | | |_) | |\\/| |")
    print(" | |_| |  __/| |  | |")
    print(" |____/|_|   |_|  |_|")
    print()
    print(" Dependency Package Manager")
    print()
    print(f"Usage: {program_name} <command> [packages...]")
    print()
    print("Commands:")
    print("  install   <packages...>  Install packages and dependencies")
    print("  update    <packages...>  Update packages to latest versions")
    print("  remove    <packages...>  Remove installed packages")
    print("  list                     List all installed packages")
    print("  resolve   <packages...>  Show resolution plan (dry run)")
    print("  tree      <packages...>  Show dependency tree")
    print("  lock      <packages...>  Generate lock file without installing")
    print("  search    <query>        Search for packages")
    print("  info      <package>      Show package information")
    print("  venv      [command]      Manage virtual environment")
    print("  init                     Initialize dpm.json manifest file")
    print("  clean                    Remove unused packages")
    print("  outdated                 Check for outdated packages")
    print("  cache                    Manage cache (clear, info, list)")
    print("  pin      <pkg>@<version> Pin package to exact version")
    print("  unpin    <pkg>           Unpin package (allow version ranges)")
    print("  export   <format>        Export dependencies (requirements.txt, package.json)")
    print("  repo     [command]        Manage custom repositories")
    print()
    print("Options:")
    print("  --verbose, -v            Verbose output")
    print("  --debug, -d              Debug output (includes verbose)")
    print("  --offline                Offline mode (use cache only)")
    print("  --skip-integrity         Skip integrity verification")
    print("  --show-resolution        Show detailed resolution steps")
    print()
    print("Examples:")
    print(f"  dpm install numpy pandas matplotlib")
    print(f"  dpm resolve flask django")
    print(f"  dpm list")
    print()


def print_version():
    """print version information"""
    print("DPM version 1.0.0")
    print("Cross-language dependency package manager")


def main():
    """main entry point"""
    parser = argparse.ArgumentParser(prog='dpm', add_help=False)
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--debug', '-d', action='store_true', help='debug output')
    parser.add_argument('--offline', action='store_true', help='offline mode (use cache only)')
    parser.add_argument('--skip-integrity', action='store_true', help='skip integrity verification')
    parser.add_argument('--show-resolution', action='store_true', help='show detailed resolution steps')
    
    # parse known args to extract flags, rest goes to command
    args, remaining = parser.parse_known_args()
    
    if len(remaining) < 1:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 1
    
    command = remaining[0]
    packages = remaining[1:] if len(remaining) > 1 else []
    
    # handle special flags
    if command in ["--help", "-h"]:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 0
    
    if command in ["--version", "-V"]:
        print_version()
        return 0
    
    handler = CommandHandler(
        verbose=args.verbose, 
        debug=args.debug, 
        offline=args.offline, 
        skip_integrity=args.skip_integrity,
        show_resolution=args.show_resolution
    )
    
    if command in ["install", "i"]:
        return handler.handle_install(packages)
    elif command in ["update", "u"]:
        return handler.handle_update(packages)
    elif command in ["remove", "rm", "uninstall"]:
        return handler.handle_remove(packages)
    elif command in ["list", "ls"]:
        return handler.handle_list()
    elif command in ["resolve", "r"]:
        return handler.handle_resolve(packages)
    elif command in ["tree", "t"]:
        return handler.handle_tree(packages)
    elif command == "lock":
        return handler.handle_lock(packages)
    elif command in ["search", "s"]:
        if not packages:
            print("Error: No search query specified")
            return 1
        return handler.handle_search(packages[0])
    elif command == "info":
        if not packages:
            print("Error: No package specified")
            return 1
        return handler.handle_info(packages[0])
    elif command == "venv":
        return handler.handle_venv(packages)
    elif command == "init":
        return handler.handle_init(packages)
    elif command == "clean":
        return handler.handle_clean(packages)
    elif command == "outdated":
        return handler.handle_outdated(packages)
    elif command == "cache":
        return handler.handle_cache(packages)
    elif command == "pin":
        return handler.handle_pin(packages)
    elif command == "unpin":
        return handler.handle_unpin(packages)
    elif command == "export":
        return handler.handle_export(packages)
    elif command == "repo":
        return handler.handle_repo(packages)
    else:
        print(f"Error: Unknown command: {command}")
        print()
        print(f"Run {sys.argv[0] if sys.argv else 'dpm'} --help for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


main.py - entry point for dpm
"""

import sys
import argparse
from .cli.commands import CommandHandler


def print_usage(program_name: str):
    """print usage information"""
    print()
    print("  ____  ____  __  __ ")
    print(" |  _ \\|  _ \\|  \\/  |")
    print(" | | | | |_) | |\\/| |")
    print(" | |_| |  __/| |  | |")
    print(" |____/|_|   |_|  |_|")
    print()
    print(" Dependency Package Manager")
    print()
    print(f"Usage: {program_name} <command> [packages...]")
    print()
    print("Commands:")
    print("  install   <packages...>  Install packages and dependencies")
    print("  update    <packages...>  Update packages to latest versions")
    print("  remove    <packages...>  Remove installed packages")
    print("  list                     List all installed packages")
    print("  resolve   <packages...>  Show resolution plan (dry run)")
    print("  tree      <packages...>  Show dependency tree")
    print("  lock      <packages...>  Generate lock file without installing")
    print("  search    <query>        Search for packages")
    print("  info      <package>      Show package information")
    print("  venv      [command]      Manage virtual environment")
    print("  init                     Initialize dpm.json manifest file")
    print("  clean                    Remove unused packages")
    print("  outdated                 Check for outdated packages")
    print("  cache                    Manage cache (clear, info, list)")
    print("  pin      <pkg>@<version> Pin package to exact version")
    print("  unpin    <pkg>           Unpin package (allow version ranges)")
    print("  export   <format>        Export dependencies (requirements.txt, package.json)")
    print("  repo     [command]        Manage custom repositories")
    print()
    print("Options:")
    print("  --verbose, -v            Verbose output")
    print("  --debug, -d              Debug output (includes verbose)")
    print("  --offline                Offline mode (use cache only)")
    print("  --skip-integrity         Skip integrity verification")
    print("  --show-resolution        Show detailed resolution steps")
    print()
    print("Examples:")
    print(f"  dpm install numpy pandas matplotlib")
    print(f"  dpm resolve flask django")
    print(f"  dpm list")
    print()


def print_version():
    """print version information"""
    print("DPM version 1.0.0")
    print("Cross-language dependency package manager")


def main():
    """main entry point"""
    parser = argparse.ArgumentParser(prog='dpm', add_help=False)
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--debug', '-d', action='store_true', help='debug output')
    parser.add_argument('--offline', action='store_true', help='offline mode (use cache only)')
    parser.add_argument('--skip-integrity', action='store_true', help='skip integrity verification')
    parser.add_argument('--show-resolution', action='store_true', help='show detailed resolution steps')
    
    # parse known args to extract flags, rest goes to command
    args, remaining = parser.parse_known_args()
    
    if len(remaining) < 1:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 1
    
    command = remaining[0]
    packages = remaining[1:] if len(remaining) > 1 else []
    
    # handle special flags
    if command in ["--help", "-h"]:
        print_usage(sys.argv[0] if sys.argv else "dpm")
        return 0
    
    if command in ["--version", "-V"]:
        print_version()
        return 0
    
    handler = CommandHandler(
        verbose=args.verbose, 
        debug=args.debug, 
        offline=args.offline, 
        skip_integrity=args.skip_integrity,
        show_resolution=args.show_resolution
    )
    
    if command in ["install", "i"]:
        return handler.handle_install(packages)
    elif command in ["update", "u"]:
        return handler.handle_update(packages)
    elif command in ["remove", "rm", "uninstall"]:
        return handler.handle_remove(packages)
    elif command in ["list", "ls"]:
        return handler.handle_list()
    elif command in ["resolve", "r"]:
        return handler.handle_resolve(packages)
    elif command in ["tree", "t"]:
        return handler.handle_tree(packages)
    elif command == "lock":
        return handler.handle_lock(packages)
    elif command in ["search", "s"]:
        if not packages:
            print("Error: No search query specified")
            return 1
        return handler.handle_search(packages[0])
    elif command == "info":
        if not packages:
            print("Error: No package specified")
            return 1
        return handler.handle_info(packages[0])
    elif command == "venv":
        return handler.handle_venv(packages)
    elif command == "init":
        return handler.handle_init(packages)
    elif command == "clean":
        return handler.handle_clean(packages)
    elif command == "outdated":
        return handler.handle_outdated(packages)
    elif command == "cache":
        return handler.handle_cache(packages)
    elif command == "pin":
        return handler.handle_pin(packages)
    elif command == "unpin":
        return handler.handle_unpin(packages)
    elif command == "export":
        return handler.handle_export(packages)
    elif command == "repo":
        return handler.handle_repo(packages)
    else:
        print(f"Error: Unknown command: {command}")
        print()
        print(f"Run {sys.argv[0] if sys.argv else 'dpm'} --help for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

