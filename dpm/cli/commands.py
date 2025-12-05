"""
commands.py - handles all the commands the user types
"""

from typing import List, Dict, Set
from ..resolver.resolver import DependencyResolver
from ..installer.installer import Installer
from ..installer.state import PackageState
from ..installer.lockfile import LockFile
from ..installer.venv import VirtualEnv
from ..sources.source import Source
from ..sources.pypi import PyPISource
from ..sources.npm import NpmSource
from ..sources.system import SystemSource
from ..sources.local import LocalSource
from ..network.cache import Cache
from ..core.package import Package
from ..core.manifest import Manifest
from ..core.progress import ProgressBar, Color, success, error, warning, info
from ..installer.integrity import Integrity
from ..core.errors import PackageNotFoundError, DependencyConflictError, NetworkError
from ..core.exporter import Exporter
from ..core.config import Config
from ..core.logger import Logger
from ..installer.plan import InstallationPlan
from ..core.repository import RepositoryManager
import logging

logger = logging.getLogger(__name__)


class CommandHandler:
    """handles all the cli commands"""
    
    def __init__(self, verbose: bool = False, debug: bool = False, offline: bool = False, skip_integrity: bool = False, show_resolution: bool = False):
        self.verbose = verbose
        self.debug = debug
        self.offline = offline
        self.show_resolution = show_resolution
        self.cache = Cache()
        self.sources: List[Source] = []
        self.resolver = DependencyResolver()
        self.installer = Installer(skip_integrity=skip_integrity)
        self.state = PackageState()
        self.lockfile = LockFile()
        self.venv = VirtualEnv()
        self.manifest = Manifest()
        self.exporter = Exporter(self.manifest, self.lockfile)
        self.config = Config()
        self.repo_manager = RepositoryManager()
        self._initialize_sources()
        
        if self.offline:
            # set offline mode on http client
            from ..network.http_client import HttpClient
            # update sources to use offline http client
            for source in self.sources:
                if hasattr(source, 'http_client'):
                    source.http_client.offline = True
        
        if self.debug:
            self.verbose = True  # debug implies verbose
    
    def _initialize_sources(self):
        """set up package sources (pypi, npm, etc)"""
        self.sources = [
            PyPISource(self.cache),
            NpmSource(self.cache),
            SystemSource(),
            LocalSource()
        ]
        
        # add custom repositories
        from ..sources.custom_repo import CustomRepositorySource
        custom_repos = self.repo_manager.list()
        for repo in custom_repos:
            try:
                custom_source = CustomRepositorySource(repo, self.cache)
                self.sources.append(custom_source)
                if self.verbose:
                    print(f"Added custom repository: {repo.name} ({repo.url})")
            except Exception as e:
                logger.warning(f"Failed to initialize custom repository {repo.name}: {e}")
    
    def handle_install(self, packages: List[str]) -> int:
        """dpm install <packages>"""
        # if no packages specified, try to install from lock file or manifest
        if not packages:
            # first try lock file
            if self.lockfile.exists():
                info("Installing from lock file...")
                locked_versions = self.lockfile.get_locked_versions()
                if not locked_versions:
                    error("Lock file is empty or invalid")
                    return 1
                
                print(f"Found {len(locked_versions)} packages in lock file")
                print(f"\n{Color.CYAN}Installing packages...{Color.RESET}")
                progress = ProgressBar(len(locked_versions), "Installing", width=30)
                installed_count = 0
                
                for i, (name, version) in enumerate(locked_versions.items()):
                    progress.update(i)
                    # find the package to get language info
                    package = None
                    for source in self.sources:
                        pkg = source.fetch_package(name, version)
                        if pkg:
                            package = pkg
                            break
                    
                    if package:
                        if self.installer.install(package):
                            self.state.add_package(name, version)
                            installed_count += 1
                        else:
                            progress.finish()
                            error(f"Failed to install {name}@{version}")
                            return 1
                    else:
                        progress.finish()
                        error(f"Package {name}@{version} not found in any source")
                        return 1
                
                progress.finish()
                success(f"Installation complete! Installed {installed_count} packages")
                return 0
            # then try manifest file
            elif self.manifest.exists():
                info("Installing from manifest file (dpm.json)...")
                deps = self.manifest.get_dependencies()
                if not deps:
                    error("No dependencies found in manifest file")
                    return 1
                
                # convert manifest dependencies to package list
                packages = list(deps.keys())
                print(f"Found {len(packages)} dependencies in manifest")
                # continue with normal installation flow below
            else:
                error("No packages specified and no lock file or manifest found")
                print(f"  Use: {Color.CYAN}dpm install <packages>{Color.RESET}")
                print(f"  Or:  {Color.CYAN}dpm init{Color.RESET} to create dpm.json")
                print(f"  Or:  {Color.CYAN}dpm lock <packages>{Color.RESET} then {Color.CYAN}dpm install{Color.RESET}")
                return 1
        
        print(f"{Color.CYAN}Resolving dependencies{Color.RESET} for: {', '.join(packages)}")
        self.logger.info(f"Resolving dependencies for: {', '.join(packages)}")
        if self.offline:
            warning("Offline mode: using cached data only")
            self.logger.warning("Offline mode enabled")
        if self.verbose:
            info(f"Using sources: {', '.join(s.get_name() for s in self.sources)}")
            self.logger.debug(f"Using sources: {', '.join(s.get_name() for s in self.sources)}")
        
        result = self.resolver.resolve(packages, self.sources)
        self.logger.info(f"Resolution {'succeeded' if result.success else 'failed'}: {len(result.selected_versions)} packages")
        
        if not result.success:
            # try to provide better error context
            error_msg = result.error_message
            if "not found" in error_msg.lower():
                # try to extract package name
                for pkg in packages:
                    if pkg in error_msg:
                        source_names = [s.get_name() for s in self.sources]
                        try:
                            raise PackageNotFoundError(pkg, source_names)
                        except PackageNotFoundError as e:
                            error(str(e))
                            return 1
            
            if "conflict" in error_msg.lower() or "constraint" in error_msg.lower():
                # provide conflict details if available
                conflict_details = result.conflict_details or {}
                try:
                    raise DependencyConflictError(
                        packages[0] if packages else "unknown",
                        conflict_details
                    )
                except DependencyConflictError as e:
                    error(str(e))
                    if self.verbose and conflict_details:
                        print(f"\n{Color.YELLOW}Conflict Details:{Color.RESET}")
                        for pkg, conflicts in conflict_details.items():
                            print(f"  {pkg}: {', '.join(conflicts)}")
                    return 1
            
            error(error_msg)
            if self.debug:
                import traceback
                traceback.print_exc()
            return 1
        
        print(f"\n{Color.GREEN}Resolved{Color.RESET} {len(result.selected_versions)} packages")
        if result.used_backtracking:
            warning("Used backtracking to resolve conflicts")
        if self.verbose or self.show_resolution:
            info(f"Resolution algorithm: {'backtracking' if result.used_backtracking else 'greedy'}")
            if self.show_resolution:
                print(f"\n{Color.CYAN}Resolution Details:{Color.RESET}")
                print(f"  Packages requested: {len(packages)}")
                print(f"  Total packages resolved: {len(result.selected_versions)}")
                print(f"  Algorithm used: {'Backtracking (conflict resolution)' if result.used_backtracking else 'Greedy (fast path)'}")
                if result.conflict_details:
                    print(f"  Conflicts detected: {len(result.conflict_details)}")
                    for pkg, conflicts in result.conflict_details.items():
                        print(f"    - {pkg}: {', '.join(conflicts)}")
        
        # build dependency map and package info for lock file
        dep_map = self._build_dependency_map(result)
        pkg_info = self._build_package_info(result)
        
        # create installation plan
        plan = InstallationPlan(result.selected_versions, dep_map)
        ordered = plan.get_ordered_packages()
        
        if self.verbose:
            info(f"Installation order: {len(ordered)} packages")
            if self.show_resolution:
                parallel_groups = plan.get_parallel_groups()
                info(f"Can install {len(parallel_groups)} groups in parallel")
        
        print(f"\n{Color.CYAN}Installing packages...{Color.RESET}")
        progress = ProgressBar(len(ordered), "Installing", width=30)
        installed_count = 0
        
        for i, (name, version) in enumerate(ordered):
            progress.update(i)
            if self.verbose:
                info(f"Installing {name}@{version}...")
            
            # find the package to get language info
            package = None
            for source in self.sources:
                pkg = source.fetch_package(name, version)
                if pkg:
                    package = pkg
                    break
            
            if package:
                if self.verbose and package.integrity:
                    info(f"  Integrity: {package.integrity}")
                if self.installer.install(package):
                    self.state.add_package(name, version)
                    installed_count += 1
                    if self.debug:
                        info(f"  Successfully installed {name}@{version}")
                else:
                    progress.finish()
                    error(f"Failed to install {name}@{version}")
                    if self.debug:
                        import traceback
                        traceback.print_exc()
                    return 1
        
        progress.finish()
        
        # write lock file
        self.lockfile.write(result.selected_versions, dep_map, pkg_info)
        
        # update manifest file if it exists
        if self.manifest.exists():
            for name, version in result.selected_versions.items():
                # only update if it was in the original request
                if name in packages:
                    self.manifest.add_dependency(name, f"=={version}")
        
        success(f"Installation complete! Installed {installed_count} packages")
        return 0
    
    def handle_resolve(self, packages: List[str]) -> int:
        """dpm resolve - dry run, shows what would be installed"""
        if not packages:
            error("No packages specified")
            return 1
        
        print(f"{Color.CYAN}Resolving dependencies{Color.RESET} for: {', '.join(packages)}")
        result = self.resolver.resolve(packages, self.sources)
        
        if not result.success:
            error(result.error_message)
            return 1
        
        print(f"\n{Color.GREEN}Resolved{Color.RESET} {len(result.selected_versions)} packages:")
        for name, version in sorted(result.selected_versions.items()):
            print(f"  {Color.CYAN}*{Color.RESET} {Color.BOLD}{name}{Color.RESET}@{version}")
        
        if result.used_backtracking:
            warning("Used backtracking to resolve conflicts")
        
        return 0
    
    def handle_list(self) -> int:
        """dpm list - shows installed packages"""
        installed = self.state.get_all_installed()
        
        if not installed:
            info("No packages installed")
            return 0
        
        print(f"{Color.CYAN}Installed packages{Color.RESET} ({len(installed)}):")
        for name, version in sorted(installed.items()):
            print(f"  {Color.CYAN}*{Color.RESET} {Color.BOLD}{name}{Color.RESET}@{version}")
        
        return 0
    
    def handle_search(self, query: str) -> int:
        """dpm search <query>"""
        print(f"{Color.CYAN}Searching for:{Color.RESET} {query}\n")
        
        all_results = []
        
        # search in all sources
        for source in self.sources:
            if hasattr(source, 'search'):
                results = source.search(query, limit=10)
                for result in results:
                    result['source'] = source.get_name()
                    all_results.append(result)
        
        if not all_results:
            warning("No packages found")
            return 0
        
        print(f"{Color.GREEN}Found{Color.RESET} {len(all_results)} packages:\n")
        for result in all_results[:20]:  # limit to 20 results
            name = result.get('name', '')
            version = result.get('version', '')
            desc = result.get('description', '')
            source = result.get('source', '')
            
            print(f"  {Color.CYAN}*{Color.RESET} {Color.BOLD}{name}{Color.RESET}@{version} {Color.DIM}({source}){Color.RESET}")
            if desc:
                print(f"    {Color.DIM}{desc[:80]}...{Color.RESET}")
            print()
        
        return 0
    
    def handle_info(self, package_name: str) -> int:
        """dpm info <package> - shows package details"""
        # find package in sources
        package = None
        source_name = ""
        
        for source in self.sources:
            if source.package_exists(package_name):
                package = source.fetch_latest(package_name)
                source_name = source.get_name()
                break
        
        if not package:
            error(f"Package '{package_name}' not found")
            return 1
        
        print(f"{Color.BOLD}Package:{Color.RESET} {Color.CYAN}{package.name}{Color.RESET}")
        print(f"{Color.BOLD}Version:{Color.RESET} {package.version}")
        print(f"{Color.BOLD}Language:{Color.RESET} {package.language}")
        print(f"{Color.BOLD}Source:{Color.RESET} {source_name}")
        
        if package.dependencies:
            print(f"\n{Color.BOLD}Dependencies{Color.RESET} ({len(package.dependencies)}):")
            for dep in package.dependencies:
                print(f"  {Color.CYAN}*{Color.RESET} {dep}")
        else:
            print(f"\n{Color.DIM}No dependencies{Color.RESET}")
        
        return 0
    
    def handle_tree(self, packages: List[str]) -> int:
        """dpm tree - shows dependency tree"""
        if not packages:
            # show tree for all installed packages
            installed = self.state.get_all_installed()
            if not installed:
                print("No packages installed")
                return 0
            packages = list(installed.keys())
        
        # resolve dependencies
        result = self.resolver.resolve(packages, self.sources)
        if not result.success:
            print(f"Error: {result.error_message}")
            return 1
        
        # build dependency map
        dep_map = self._build_dependency_map(result)
        
        print("Dependency tree:\n")
        visited = set()
        for pkg in packages:
            if pkg not in visited:
                self._print_tree(pkg, result.selected_versions, dep_map, "", True, visited)
        
        return 0
    
    def _print_tree(self, pkg: str, versions: Dict[str, str], dep_map: Dict[str, List[str]],
                   prefix: str, is_last: bool, visited: Set[str]):
        """recursively prints dependency tree with nice formatting"""
        if pkg in visited:
            return
        visited.add(pkg)
        
        version = versions.get(pkg, "?")
        connector = "`-- " if is_last else "|-- "
        print(f"{prefix}{connector}{pkg}@{version}")
        
        deps = dep_map.get(pkg, [])
        if deps:
            new_prefix = prefix + ("    " if is_last else "|   ")
            for i, dep in enumerate(deps):
                is_last_dep = (i == len(deps) - 1)
                self._print_tree(dep, versions, dep_map, new_prefix, is_last_dep, visited)
    
    def handle_lock(self, packages: List[str]) -> int:
        """dpm lock - creates lock file without installing"""
        if not packages:
            print("Error: No packages specified")
            return 1
        
        print(f"Resolving dependencies for: {', '.join(packages)}")
        result = self.resolver.resolve(packages, self.sources)
        
        if not result.success:
            error(result.error_message)
            return 1
        
        dep_map = self._build_dependency_map(result)
        pkg_info = self._build_package_info(result)
        
        if self.lockfile.write(result.selected_versions, dep_map, pkg_info):
            success(f"Lock file written to {self.lockfile.lockfile_path}")
            print(f"Locked {len(result.selected_versions)} packages")
            return 0
        else:
            error("Failed to write lock file")
            return 1
    
    def handle_update(self, packages: List[str]) -> int:
        """dpm update <packages>"""
        if not packages:
            # update all installed packages
            installed = self.state.get_all_installed()
            if not installed:
                info("No packages installed to update")
                return 0
            packages = list(installed.keys())
            info(f"Updating {len(packages)} installed packages...")
        
        # update is basically re-install with latest versions
        return self.handle_install(packages)
    
    def handle_remove(self, packages: List[str]) -> int:
        """dpm remove <packages>"""
        if not packages:
            print("Error: No packages specified")
            return 1
        
        removed_count = 0
        progress = ProgressBar(len(packages), "Removing", width=30)
        
        for i, pkg_name in enumerate(packages):
            progress.update(i)
            if not self.state.is_installed(pkg_name):
                warning(f"Package not installed: {pkg_name}")
                continue
            
            version = self.state.get_installed_version(pkg_name)
            
            # find package to get language info
            package = None
            for source in self.sources:
                if source.package_exists(pkg_name):
                    pkg = source.fetch_package(pkg_name, version or "latest")
                    if pkg:
                        package = pkg
                        break
            
            if package:
                if self.installer.uninstall(package):
                    self.state.remove_package(pkg_name)
                    removed_count += 1
                else:
                    progress.finish()
                    error(f"Failed to remove {pkg_name}")
                    return 1
        
        progress.finish()
        success(f"Removed {removed_count} packages")
        return 0
    
    def handle_venv(self, args: List[str]) -> int:
        """dpm venv - manage virtual environment"""
        if not args:
            print("Usage: dpm venv <command> [args...]")
            print("Commands:")
            print("  create <name> [path]  Create virtual environment")
            print("  status                 Show venv status")
            print("  remove                 Remove current venv")
            print("  detect                 Detect active environment")
            print("  use <type> [path]      Use existing environment")
            return 1
        
        command = args[0]
        
        if command == "create":
            if len(args) < 2:
                error("venv name required")
                return 1
            name = args[1]
            path = args[2] if len(args) > 2 else None
            
            print(f"{Color.CYAN}Creating virtual environment:{Color.RESET} {name}")
            if self.venv.create(name, path):
                success("Virtual environment created")
                status = self.venv.status()
                if status:
                    print(f"  Path: {status.get('path', '')}")
                    if status.get('activate_script'):
                        print(f"  Activate with: {Color.CYAN}source {status['activate_script']}{Color.RESET}")
                return 0
            else:
                error("Failed to create virtual environment")
                return 1
        
        elif command == "status":
            status = self.venv.status()
            if status:
                print(f"{Color.CYAN}Virtual environment status:{Color.RESET}")
                print(f"  Active: {status.get('active', 'false')}")
                print(f"  Path: {status.get('path', '')}")
            else:
                # try to detect
                detected = self.venv.detect_environment()
                if detected:
                    info(f"Detected {detected['type']} environment: {detected.get('path', detected.get('name', ''))}")
                else:
                    info("No virtual environment found")
            return 0
        
        elif command == "detect":
            detected = self.venv.detect_environment()
            if detected:
                print(f"{Color.GREEN}Detected environment:{Color.RESET}")
                print(f"  Type: {detected['type']}")
                if 'name' in detected:
                    print(f"  Name: {detected['name']}")
                print(f"  Path: {detected.get('path', '')}")
            else:
                info("No environment detected")
            return 0
        
        elif command == "use":
            if len(args) < 2:
                error("Environment type required (conda, poetry, pipenv, venv, auto)")
                return 1
            env_type = args[1]
            path = args[2] if len(args) > 2 else None
            
            if self.venv.use_environment(env_type, path):
                success(f"Using {env_type} environment")
                return 0
            else:
                error(f"Failed to use {env_type} environment")
                return 1
        
        elif command == "remove":
            if self.venv.remove():
                success("Virtual environment removed")
                return 0
            else:
                error("Failed to remove virtual environment")
                return 1
        
        else:
            error(f"Unknown venv command: {command}")
            return 1
    
    def _build_dependency_map(self, result) -> Dict[str, List[str]]:
        """builds map of package -> dependencies for lock file"""
        dep_map = {}
        
        for name, version in result.selected_versions.items():
            # find package to get dependencies
            package = None
            for source in self.sources:
                pkg = source.fetch_package(name, version)
                if pkg:
                    package = pkg
                    break
            
            if package:
                dep_map[name] = [dep.name for dep in package.dependencies]
            else:
                dep_map[name] = []
        
        return dep_map
    
    def _build_package_info(self, result) -> Dict[str, Dict[str, str]]:
        """builds map of package -> (language, source, integrity)"""
        pkg_info = {}
        
        for name, version in result.selected_versions.items():
            # find package to get language and source
            package = None
            source_name = ""
            for source in self.sources:
                pkg = source.fetch_package(name, version)
                if pkg:
                    package = pkg
                    source_name = source.get_name()
                    break
            
            if package:
                pkg_info[name] = {
                    "language": package.language,
                    "source": source_name,
                    "integrity": package.integrity
                }
            else:
                pkg_info[name] = {
                    "language": "unknown",
                    "source": "unknown",
                    "integrity": None
                }
        
        return pkg_info
    
    def handle_init(self, args: List[str]) -> int:
        """dpm init - initialize dpm.json manifest file"""
        if self.manifest.exists():
            print("Error: dpm.json already exists")
            response = input("Overwrite? (y/N): ").strip().lower()
            if response != 'y':
                print("Cancelled")
                return 1
        
        # get project name from args or prompt
        name = args[0] if args else input("Project name [my-project]: ").strip() or "my-project"
        version = args[1] if len(args) > 1 else input("Version [1.0.0]: ").strip() or "1.0.0"
        
        if self.manifest.create_template(name, version):
            print(f"Created dpm.json for {name}@{version}")
            return 0
        else:
            print("Error: Failed to create dpm.json")
            return 1
    
    def handle_clean(self, args: List[str]) -> int:
        """dpm clean - remove unused packages"""
        dry_run = "--dry-run" in args or "-n" in args
        if dry_run:
            args = [a for a in args if a not in ["--dry-run", "-n"]]
        
        # get installed packages
        installed = self.state.get_all_installed()
        if not installed:
            info("No packages installed")
            return 0
        
        # get declared packages from manifest or lock file
        declared = set()
        
        if self.lockfile.exists():
            locked = self.lockfile.get_locked_packages()
            declared.update(locked)
        
        if self.manifest.exists():
            deps = self.manifest.get_dependencies()
            declared.update(deps.keys())
            dev_deps = self.manifest.get_dev_dependencies()
            declared.update(dev_deps.keys())
        
        # find unused packages
        unused = set(installed.keys()) - declared
        
        if not unused:
            info("No unused packages found")
            return 0
        
        if dry_run:
            print(f"{Color.YELLOW}Would remove{Color.RESET} {len(unused)} unused packages:")
            for pkg in sorted(unused):
                print(f"  {Color.CYAN}*{Color.RESET} {pkg}@{installed[pkg]}")
            return 0
        
        print(f"{Color.YELLOW}Removing{Color.RESET} {len(unused)} unused packages...")
        progress = ProgressBar(len(unused), "Removing", width=30)
        removed_count = 0
        
        for i, pkg_name in enumerate(sorted(unused)):
            progress.update(i)
            version = installed[pkg_name]
            
            # find package to get language info
            package = None
            for source in self.sources:
                if source.package_exists(pkg_name):
                    pkg = source.fetch_package(pkg_name, version or "latest")
                    if pkg:
                        package = pkg
                        break
            
            if package:
                if self.installer.uninstall(package):
                    self.state.remove_package(pkg_name)
                    removed_count += 1
                else:
                    progress.finish()
                    error(f"Failed to remove {pkg_name}")
                    return 1
        
        progress.finish()
        success(f"Removed {removed_count} unused packages")
        return 0
    
    def handle_outdated(self, packages: List[str]) -> int:
        """dpm outdated - check for outdated packages"""
        # get installed packages
        if packages:
            installed = {pkg: self.state.get_installed_version(pkg) for pkg in packages if self.state.is_installed(pkg)}
        else:
            installed = self.state.get_all_installed()
        
        if not installed:
            info("No packages installed")
            return 0
        
        print(f"{Color.CYAN}Checking for outdated packages...{Color.RESET}\n")
        
        outdated = []
        up_to_date = []
        
        for name, installed_version in installed.items():
            # find source and get latest version
            latest_version = None
            source_name = ""
            
            for source in self.sources:
                if source.package_exists(name):
                    pkg = source.fetch_latest(name)
                    if pkg:
                        latest_version = pkg.version
                        source_name = source.get_name()
                        break
            
            if not latest_version:
                warning(f"Could not check {name} - not found in any source")
                continue
            
            # compare versions
            from ..core.version import Version
            try:
                installed_v = Version(installed_version)
                latest_v = Version(latest_version)
                
                if latest_v > installed_v:
                    outdated.append((name, installed_version, latest_version, source_name))
                else:
                    up_to_date.append((name, installed_version))
            except ValueError:
                # can't compare versions, assume up to date
                up_to_date.append((name, installed_version))
        
        if outdated:
            print(f"{Color.YELLOW}Outdated packages{Color.RESET} ({len(outdated)}):\n")
            for name, installed_v, latest_v, source in outdated:
                print(f"  {Color.CYAN}*{Color.RESET} {Color.BOLD}{name}{Color.RESET}")
                print(f"    Installed: {installed_v} -> Latest: {Color.GREEN}{latest_v}{Color.RESET} ({source})")
            print()
        
        if up_to_date:
            if self.verbose:
                print(f"{Color.GREEN}Up to date{Color.RESET} ({len(up_to_date)}):")
                for name, version in up_to_date:
                    print(f"  {Color.CYAN}*{Color.RESET} {name}@{version}")
                print()
        
        if not outdated:
            success("All packages are up to date!")
            return 0
        
        info(f"Run {Color.CYAN}dpm update{Color.RESET} to update outdated packages")
        return 0
    
    def handle_cache(self, args: List[str]) -> int:
        """dpm cache - manage cache"""
        if not args:
            args = ["info"]
        
        command = args[0]
        
        if command == "clear":
            response = input(f"{Color.YELLOW}Clear all cached data? (y/N): {Color.RESET}").strip().lower()
            if response == 'y':
                self.cache.clear()
                success("Cache cleared")
                return 0
            else:
                info("Cancelled")
                return 0
        
        elif command == "info":
            info_dict = self.cache.get_info()
            print(f"{Color.CYAN}Cache Information:{Color.RESET}")
            print(f"  Location: {info_dict['location']}")
            print(f"  Files: {info_dict['file_count']}")
            print(f"  Size: {info_dict['total_size_mb']} MB ({info_dict['total_size']} bytes)")
            return 0
        
        elif command == "list":
            cached = self.cache.list_cached()
            if not cached:
                info("Cache is empty")
                return 0
            
            print(f"{Color.CYAN}Cached packages{Color.RESET} ({len(cached)}):")
            for item in sorted(cached)[:50]:  # limit to 50
                print(f"  {Color.CYAN}*{Color.RESET} {item}")
            if len(cached) > 50:
                print(f"  ... and {len(cached) - 50} more")
            return 0
        
        else:
            error(f"Unknown cache command: {command}")
            print(f"  Use: {Color.CYAN}dpm cache clear{Color.RESET}")
            print(f"  Use: {Color.CYAN}dpm cache info{Color.RESET}")
            print(f"  Use: {Color.CYAN}dpm cache list{Color.RESET}")
            return 1
    
    def handle_pin(self, packages: List[str]) -> int:
        """dpm pin <package>@<version> - pin package to exact version"""
        if not packages:
            error("No package specified")
            print(f"  Use: {Color.CYAN}dpm pin <package>@<version>{Color.RESET}")
            return 1
        
        pkg_spec = packages[0]
        if '@' not in pkg_spec:
            error("Invalid format. Use: package@version")
            return 1
        
        name, version = pkg_spec.split('@', 1)
        
        # ensure manifest exists
        if not self.manifest.exists():
            if not self.manifest.create_template():
                error("Failed to create dpm.json")
                return 1
        
        # pin in manifest
        if self.manifest.add_dependency(name, f"=={version}"):
            success(f"Pinned {name} to {version}")
            return 0
        else:
            error(f"Failed to pin {name}")
            return 1
    
    def handle_unpin(self, packages: List[str]) -> int:
        """dpm unpin <package> - unpin package"""
        if not packages:
            error("No package specified")
            return 1
        
        name = packages[0]
        
        if not self.manifest.exists():
            error("No manifest file found")
            return 1
        
        # get current dependency
        deps = self.manifest.get_dependencies()
        if name not in deps:
            warning(f"Package {name} not found in manifest")
            return 0
        
        current = deps[name]
        
        # if it's pinned (==version), change to ^version (allow minor updates)
        if current.startswith("=="):
            version = current[2:]
            if self.manifest.add_dependency(name, f"^{version}"):
                success(f"Unpinned {name}, now allows minor updates (^{version})")
                return 0
        
        info(f"{name} is not pinned")
        return 0
    
    def handle_export(self, args: List[str]) -> int:
        """dpm export <format> [output] - export dependencies"""
        if not args:
            error("No format specified")
            print(f"  Formats: {Color.CYAN}requirements.txt{Color.RESET}, {Color.CYAN}package.json{Color.RESET}, {Color.CYAN}lock{Color.RESET}")
            return 1
        
        format_type = args[0].lower()
        output_path = args[1] if len(args) > 1 else None
        
        if format_type == "requirements.txt" or format_type == "requirements":
            output = output_path or "requirements.txt"
            if self.exporter.export_requirements_txt(output):
                success(f"Exported to {output}")
                return 0
            else:
                error("Failed to export. No lock file or manifest found.")
                return 1
        
        elif format_type == "package.json" or format_type == "package":
            output = output_path or "package.json"
            if self.exporter.export_package_json(output):
                success(f"Exported to {output}")
                return 0
            else:
                error("Failed to export. No manifest found.")
                return 1
        
        elif format_type == "lock":
            output = output_path or "dpm.lock.export"
            if self.exporter.export_lock(output):
                success(f"Exported lock file to {output}")
                return 0
            else:
                error("Failed to export. No lock file found.")
                return 1
        
        else:
            error(f"Unknown format: {format_type}")
            print(f"  Formats: {Color.CYAN}requirements.txt{Color.RESET}, {Color.CYAN}package.json{Color.RESET}, {Color.CYAN}lock{Color.RESET}")
            return 1
    
    def _rollback_installation(self, installed_packages: List[Package]):
        """rollback installation of packages on failure"""
        if not installed_packages:
            return
        
        warning(f"Rolling back {len(installed_packages)} installed packages...")
        for package in reversed(installed_packages):  # reverse order for rollback
            try:
                if self.installer.uninstall(package):
                    self.state.remove_package(package.name)
                    if self.verbose:
                        info(f"Rolled back {package.name}@{package.version}")
                else:
                    warning(f"Failed to rollback {package.name}@{package.version}")
            except Exception as e:
                warning(f"Error rolling back {package.name}: {e}")
    
    def handle_repo(self, args: List[str]) -> int:
        """dpm repo - manage custom repositories"""
        if not args:
            repos = self.repo_manager.list()
            if not repos:
                info("No custom repositories configured")
                return 0
            
            print(f"{Color.CYAN}Configured repositories{Color.RESET} ({len(repos)}):")
            for repo in repos:
                auth_str = " (authenticated)" if repo.auth else ""
                print(f"  {Color.CYAN}*{Color.RESET} {Color.BOLD}{repo.name}{Color.RESET}: {repo.url}{auth_str}")
            return 0
        
        command = args[0]
        
        if command == "add":
            if len(args) < 3:
                error("Usage: dpm repo add <name> <url> [username] [password]")
                return 1
            name = args[1]
            url = args[2]
            username = args[3] if len(args) > 3 else None
            password = args[4] if len(args) > 4 else None
            
            if self.repo_manager.add(name, url, username, password):
                success(f"Added repository: {name}")
                return 0
            else:
                error("Failed to add repository")
                return 1
        
        elif command == "remove":
            if len(args) < 2:
                error("Usage: dpm repo remove <name>")
                return 1
            name = args[1]
            
            if self.repo_manager.remove(name):
                success(f"Removed repository: {name}")
                return 0
            else:
                error(f"Repository not found: {name}")
                return 1
        
        elif command == "list":
            repos = self.repo_manager.list()
            if not repos:
                info("No custom repositories configured")
                return 0
            
            print(f"{Color.CYAN}Repositories{Color.RESET} ({len(repos)}):")
            for repo in repos:
                auth_str = " (authenticated)" if repo.auth else ""
                print(f"  {Color.CYAN}*{Color.RESET} {Color.BOLD}{repo.name}{Color.RESET}: {repo.url}{auth_str}")
            return 0
        
        else:
            error(f"Unknown repo command: {command}")
            print(f"  Commands: {Color.CYAN}add{Color.RESET}, {Color.CYAN}remove{Color.RESET}, {Color.CYAN}list{Color.RESET}")
            return 1
