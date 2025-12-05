# DPM Command Reference

Complete reference for all DPM commands, options, and usage examples.

## Table of Contents

1. [Installation Commands](#installation-commands)
2. [Package Management](#package-management)
3. [Dependency Resolution](#dependency-resolution)
4. [File Management](#file-management)
5. [Environment Management](#environment-management)
6. [Cache Management](#cache-management)
7. [Repository Management](#repository-management)
8. [Export/Import](#exportimport)
9. [Information Commands](#information-commands)
10. [Global Options](#global-options)

---

## Installation Commands

### `install` / `i`

Install packages and their dependencies.

**Syntax:**
```bash
dpm install [packages...]
```

**Description:**
Installs the specified packages and all their dependencies. If no packages are specified and `dpm.lock` exists, installs packages from the lock file.

**Behavior:**
- If packages are specified: Resolves and installs those packages
- If no packages specified: Installs from `dpm.lock` (if it exists)
- Updates `dpm.json` with installed packages
- Creates/updates `dpm.lock` with exact versions
- Verifies package integrity after installation
- Rolls back on failure

**Examples:**
```bash
# Install specific packages
dpm install requests flask

# Install from lock file
dpm install

# Install with verbose output
dpm install --verbose numpy pandas

# Install in offline mode (cache only)
dpm install --offline requests
```

**Exit Codes:**
- `0`: Success
- `1`: Error (package not found, conflict, installation failure)

---

### `update` / `u`

Update packages to their latest compatible versions.

**Syntax:**
```bash
dpm update [packages...]
```

**Description:**
Updates specified packages to their latest versions that satisfy constraints in `dpm.json`. If no packages are specified, updates all packages.

**Behavior:**
- Respects version constraints in `dpm.json`
- Updates dependencies if needed
- Updates `dpm.lock` with new versions
- Preserves pinned versions

**Examples:**
```bash
# Update all packages
dpm update

# Update specific packages
dpm update requests flask

# Preview what would be updated
dpm outdated
```

**Exit Codes:**
- `0`: Success
- `1`: Error (conflict, network error)

---

### `remove` / `rm` / `uninstall`

Remove installed packages.

**Syntax:**
```bash
dpm remove <packages...>
```

**Description:**
Removes the specified packages. Does not remove dependencies unless they're unused.

**Behavior:**
- Removes specified packages
- Keeps dependencies that are still needed
- Updates `dpm.json` and `dpm.lock`
- Can remove unused dependencies with `clean` command

**Examples:**
```bash
# Remove a package
dpm remove flask

# Remove multiple packages
dpm remove flask django requests

# Remove and clean unused dependencies
dpm remove flask
dpm clean
```

**Exit Codes:**
- `0`: Success
- `1`: Error (package not installed, removal failure)

---

## Package Management

### `list` / `ls`

List all installed packages.

**Syntax:**
```bash
dpm list
```

**Description:**
Shows all packages currently installed, with their versions.

**Output Format:**
```
Installed packages (5):
  * certifi@2025.11.12
  * charset_normalizer@3.4.4
  * idna@3.11
  * requests@2.32.5
  * urllib3@1.26.20
```

**Examples:**
```bash
# List installed packages
dpm list

# List with verbose output
dpm list --verbose
```

**Exit Codes:**
- `0`: Success
- `1`: Error (state file corrupted)

---

### `outdated`

Check for outdated packages.

**Syntax:**
```bash
dpm outdated
```

**Description:**
Compares installed package versions with latest available versions and reports which packages can be updated.

**Output Format:**
```
Outdated packages (1):

  * urllib3
    Installed: 1.26.20 -> Latest: 2.6.0 (PyPI)

[INFO] Run dpm update to update outdated packages
```

**Examples:**
```bash
# Check for outdated packages
dpm outdated

# Check with verbose output
dpm outdated --verbose
```

**Exit Codes:**
- `0`: Success (may show outdated packages)
- `1`: Error (network error, state file issue)

---

### `clean`

Remove unused packages.

**Syntax:**
```bash
dpm clean [--dry-run]
```

**Description:**
Removes packages that are not listed in `dpm.json` or `dpm.lock`. Use `--dry-run` to preview what would be removed.

**Options:**
- `--dry-run`: Preview what would be removed without actually removing

**Examples:**
```bash
# Preview what would be removed
dpm clean --dry-run

# Remove unused packages
dpm clean
```

**Exit Codes:**
- `0`: Success
- `1`: Error (removal failure)

---

## Dependency Resolution

### `resolve` / `r`

Show resolution plan without installing (dry run).

**Syntax:**
```bash
dpm resolve <packages...>
```

**Description:**
Resolves dependencies and shows what would be installed without actually installing. Useful for previewing dependency trees and checking for conflicts.

**Behavior:**
- Resolves dependencies using greedy or backtracking algorithm
- Shows all packages that would be installed
- Does not modify `dpm.json` or `dpm.lock`
- Does not install packages

**Examples:**
```bash
# Resolve single package
dpm resolve requests

# Resolve multiple packages
dpm resolve flask django

# Show detailed resolution steps
dpm resolve --show-resolution flask django

# Verbose output
dpm resolve --verbose requests
```

**Output Example:**
```
Resolving dependencies for: requests

Resolved 5 packages:
  * certifi@2025.11.12
  * charset_normalizer@3.4.4
  * idna@3.11
  * requests@2.32.5
  * urllib3@1.26.20
```

**Exit Codes:**
- `0`: Success (resolution found)
- `1`: Error (conflict, package not found, timeout)

---

### `tree` / `t`

Display dependency tree for packages.

**Syntax:**
```bash
dpm tree <packages...>
```

**Description:**
Shows the dependency tree for specified packages in a visual tree format.

**Output Format:**
```
Dependency tree:

`-- flask@3.1.2
    |-- blinker@1.9.0
    |-- click@8.3.1
    |   `-- colorama@0.4.6
    |-- jinja2@3.1.2
    |   `-- markupsafe@3.0.3
    `-- werkzeug@3.1.2
        `-- markupsafe@3.0.3
```

**Examples:**
```bash
# Show tree for single package
dpm tree flask

# Show tree for multiple packages
dpm tree flask django
```

**Exit Codes:**
- `0`: Success
- `1`: Error (package not found, resolution failure)

---

## File Management

### `init`

Initialize a new `dpm.json` manifest file.

**Syntax:**
```bash
dpm init [name] [version]
```

**Description:**
Creates a new `dpm.json` file for your project. If `dpm.json` already exists, prompts to overwrite.

**Arguments:**
- `name`: Project name (optional, prompts if not provided)
- `version`: Project version (optional, defaults to "1.0.0")

**Generated File:**
```json
{
  "name": "my-project",
  "version": "1.0.0",
  "description": "",
  "dependencies": {},
  "devDependencies": {},
  "sources": ["pypi", "npm"]
}
```

**Examples:**
```bash
# Initialize with name and version
dpm init myproject 1.0.0

# Initialize interactively
dpm init
```

**Exit Codes:**
- `0`: Success
- `1`: Error (file exists and not overwritten, write failure)

---

### `lock`

Generate lock file without installing packages.

**Syntax:**
```bash
dpm lock [packages...]
```

**Description:**
Resolves dependencies and creates/updates `dpm.lock` with exact versions and integrity checksums. Does not install packages.

**Behavior:**
- Resolves dependencies for specified packages
- Creates/updates `dpm.lock` with exact versions
- Includes SHA256 checksums for integrity verification
- Does not install packages
- Updates `dpm.json` if packages are specified

**Lock File Format:**
```json
{
  "version": "1.0",
  "generated": "2025-12-05T19:00:00",
  "packages": {
    "requests": {
      "version": "2.32.5",
      "language": "python",
      "source": "PyPI",
      "dependencies": ["urllib3", "certifi"],
      "integrity": "sha256:..."
    }
  }
}
```

**Examples:**
```bash
# Lock specific packages
dpm lock requests flask

# Lock all packages from dpm.json
dpm lock
```

**Exit Codes:**
- `0`: Success
- `1`: Error (resolution failure, write failure)

---

### `pin`

Pin a package to an exact version.

**Syntax:**
```bash
dpm pin <package>@<version>
```

**Description:**
Pins a package to an exact version in `dpm.json`. Prevents updates to that package.

**Examples:**
```bash
# Pin to exact version
dpm pin requests@2.32.5

# Pin multiple packages
dpm pin requests@2.32.5 flask@3.0.3
```

**Exit Codes:**
- `0`: Success
- `1`: Error (package not found, invalid version)

---

### `unpin`

Unpin a package, allowing version ranges.

**Syntax:**
```bash
dpm unpin <package>
```

**Description:**
Removes pinning from a package, allowing it to be updated within version constraints.

**Examples:**
```bash
# Unpin a package
dpm unpin requests

# Unpin multiple packages
dpm unpin requests flask
```

**Exit Codes:**
- `0`: Success
- `1`: Error (package not pinned, not in dpm.json)

---

## Environment Management

### `venv`

Manage virtual environments.

**Syntax:**
```bash
dpm venv <command> [args...]
```

**Subcommands:**

#### `create <name>`

Create a new virtual environment.

```bash
dpm venv create myenv
```

#### `detect`

Detect existing virtual environments (conda, poetry, pipenv).

```bash
dpm venv detect
```

#### `use <type>`

Use an existing environment type.

```bash
dpm venv use conda
dpm venv use poetry
dpm venv use pipenv
```

#### `status`

Check virtual environment status.

```bash
dpm venv status
```

#### `remove`

Remove the current virtual environment.

```bash
dpm venv remove
```

**Examples:**
```bash
# Create a new venv
dpm venv create myproject

# Check status
dpm venv status

# Detect existing environments
dpm venv detect
```

**Exit Codes:**
- `0`: Success
- `1`: Error (creation failure, environment not found)

---

## Cache Management

### `cache`

Manage the package metadata cache.

**Syntax:**
```bash
dpm cache <command>
```

**Subcommands:**

#### `info`

Show cache information (location, size, file count).

```bash
dpm cache info
```

**Output:**
```
Cache Information:
  Location: /Users/user/.dpm/cache
  Files: 102
  Size: 14.49 MB (15190435 bytes)
```

#### `list`

List all cached entries.

```bash
dpm cache list
```

#### `clear`

Clear all cached data.

```bash
dpm cache clear
```

**Examples:**
```bash
# Check cache status
dpm cache info

# List cached entries
dpm cache list

# Clear cache
dpm cache clear
```

**Exit Codes:**
- `0`: Success
- `1`: Error (cache operation failure)

---

## Repository Management

### `repo`

Manage custom package repositories.

**Syntax:**
```bash
dpm repo <command> [args...]
```

**Subcommands:**

#### `list`

List all configured custom repositories.

```bash
dpm repo list
```

**Output:**
```
Repositories (2):
  * company-pypi: https://pypi.company.com/pypi/
  * private-npm: https://npm.company.com/ (authenticated)
```

#### `add <name> <url> [username] [password]`

Add a custom repository.

```bash
# Add public repository
dpm repo add company-pypi https://pypi.company.com/pypi/

# Add authenticated repository
dpm repo add private-npm https://npm.company.com/ username password
```

**Repository Types:**
- **PyPI repositories**: URLs containing "pypi" or ending with "/pypi"
- **npm repositories**: URLs containing "npm" or "registry"

**Examples:**
```bash
# Add PyPI mirror
dpm repo add local-pypi https://pypi.local.com/pypi/

# Add private npm registry
dpm repo add company-npm https://npm.company.com/ user pass

# Add authenticated PyPI
dpm repo add private-pypi https://pypi.company.com/ token ""
```

#### `remove <name>`

Remove a custom repository.

```bash
dpm repo remove company-pypi
```

**How It Works:**
- Custom repositories are checked during package resolution
- Repositories are checked in order: default sources, then custom repositories
- Authentication is handled automatically for authenticated repositories
- Repositories are stored in `~/.dpm/repositories.json`

**Examples:**
```bash
# List repositories
dpm repo list

# Add repository
dpm repo add myrepo https://example.com/repo

# Remove repository
dpm repo remove myrepo
```

**Exit Codes:**
- `0`: Success
- `1`: Error (invalid URL, authentication failure, repository not found)

---

## Export/Import

### `export`

Export dependencies to other formats.

**Syntax:**
```bash
dpm export <format> [output]
```

**Description:**
Exports dependencies from `dpm.json` or `dpm.lock` to other package manager formats.

**Formats:**

#### `requirements.txt`

Export to pip requirements format.

```bash
dpm export requirements.txt
```

**Output:**
```
certifi==2025.11.12
charset_normalizer==3.4.4
idna==3.11
requests==2.32.5
urllib3==1.26.20
```

#### `package.json`

Export to npm package.json format.

```bash
dpm export package.json
```

#### `lock`

Export lock file information.

```bash
dpm export lock
```

**Examples:**
```bash
# Export to requirements.txt
dpm export requirements.txt

# Export to package.json
dpm export package.json

# Export to custom file
dpm export requirements.txt deps.txt
```

**Exit Codes:**
- `0`: Success
- `1`: Error (format not supported, write failure)

---

## Information Commands

### `search` / `s`

Search for packages across all sources.

**Syntax:**
```bash
dpm search <query>
```

**Description:**
Searches for packages matching the query across all configured sources (PyPI, npm, system, custom repositories).

**Examples:**
```bash
# Search for packages
dpm search flask

# Search with verbose output
dpm search --verbose json
```

**Output:**
```
Searching for: flask

Found 20 packages:

  * flask@3.0.3 (PyPI)
    A lightweight WSGI web application framework...

  * flask-json@1.0.0 (npm)
    Flask JSON utilities...
```

**Exit Codes:**
- `0`: Success
- `1`: Error (network error, no sources available)

---

### `info`

Show detailed information about a package.

**Syntax:**
```bash
dpm info <package>
```

**Description:**
Shows detailed information about a package, including version, dependencies, and source.

**Output:**
```
Package: requests
Version: 2.32.5
Language: python
Source: PyPI

Dependencies (4):
  * charset_normalizer<4.0.0,>=2.0.0
  * idna<4.0.0,>=2.5.0
  * urllib3<3.0.0,>=1.21.1
  * certifi>=2017.4.17
```

**Examples:**
```bash
# Get package info
dpm info requests

# Get info for npm package
dpm info express
```

**Exit Codes:**
- `0`: Success
- `1`: Error (package not found, network error)

---

## Global Options

These options can be used with any command:

### `--help` / `-h`

Show help information.

```bash
dpm --help
dpm install --help
```

### `--version`

Show DPM version.

```bash
dpm --version
```

### `--verbose` / `-v`

Show detailed output.

```bash
dpm install --verbose requests
dpm resolve --verbose flask
```

### `--debug` / `-d`

Show debug information (includes verbose).

```bash
dpm install --debug requests
```

**Debug output includes:**
- Detailed resolution steps
- Network request details
- Cache operations
- Algorithm selection (greedy vs backtracking)

### `--offline`

Use cache only, no network requests.

```bash
dpm resolve --offline requests
dpm install --offline
```

**Behavior:**
- Only uses cached package metadata
- Fails if package not in cache
- Useful for offline environments

### `--skip-integrity`

Skip integrity verification (not recommended).

```bash
dpm install --skip-integrity requests
```

**Warning:** Only use this if you trust the package source. Integrity verification prevents tampered or corrupted packages.

### `--show-resolution`

Show detailed resolution steps.

```bash
dpm resolve --show-resolution flask django
```

**Shows:**
- Which algorithm was used (greedy vs backtracking)
- Number of packages resolved
- Conflicts detected (if any)
- Resolution time

---

## Command Combinations

### Common Workflows

#### Initialize and Install

```bash
# Initialize project
dpm init myproject 1.0.0

# Install packages
dpm install requests flask

# Create lock file
dpm lock
```

#### Update Workflow

```bash
# Check for outdated packages
dpm outdated

# Update specific packages
dpm update requests

# Update all packages
dpm update
```

#### Development Workflow

```bash
# Create virtual environment
dpm venv create myenv

# Install development dependencies
dpm install pytest black

# Export for sharing
dpm export requirements.txt
```

#### Production Workflow

```bash
# Install from lock file (reproducible)
dpm install

# Verify integrity
dpm outdated  # should show no updates

# Export for deployment
dpm export requirements.txt
```

---

## Exit Codes

All commands return exit codes:

- `0`: Success
- `1`: Error (command-specific)

Common error scenarios:
- Package not found
- Dependency conflict
- Network error
- File I/O error
- Invalid input
- Timeout

---

## Tips and Best Practices

1. **Use lock files**: Always commit `dpm.lock` for reproducible installs
2. **Check before updating**: Use `dpm outdated` before `dpm update`
3. **Use virtual environments**: Isolate project dependencies
4. **Cache management**: Clear cache if you encounter stale data
5. **Offline mode**: Use `--offline` when network is unavailable
6. **Verbose output**: Use `--verbose` or `--debug` for troubleshooting
7. **Custom repositories**: Add private registries for internal packages

---

## Troubleshooting

### Command Not Found

If `dpm` command is not found:
```bash
# Use direct execution
python3 -m dpm.main --help
```

### Permission Errors

Use virtual environments or `--user` flag:
```bash
pip install --user -e .
```

### Network Errors

- Check internet connection
- Use `--offline` if cache is available
- Clear cache and retry: `dpm cache clear`

### Resolution Failures

- Use `--show-resolution` for details
- Check for version conflicts
- Try updating packages: `dpm update`

---

For more information, see:
- [Quick Start Guide](quickstart.md)
- [CLI Reference](cli.md)
- [Architecture](architecture.md)
- [Testing Guide](testing.md)

