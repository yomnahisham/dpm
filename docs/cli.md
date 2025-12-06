# CLI Reference

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `install <packages...>` | Install packages and their dependencies | `dpm install numpy pandas` |
| `update <packages...>` | Update packages to latest compatible versions | `dpm update requests` |
| `remove <packages...>` | Remove installed packages | `dpm remove flask` |
| `list` | List all installed packages | `dpm list` |
| `resolve <packages...>` | Show resolution plan without installing (dry run) | `dpm resolve django` |
| `tree <packages...>` | Display dependency tree | `dpm tree flask` |
| `lock <packages...>` | Generate lock file without installing | `dpm lock requests flask` |
| `search <query>` | Search for packages | `dpm search flask` |
| `info <package>` | Show package details | `dpm info requests` |
| `init [name] [version]` | Initialize dpm.json manifest file | `dpm init myproject 1.0.0` |
| `clean [--dry-run]` | Remove unused packages | `dpm clean` |
| `outdated` | Check for outdated packages | `dpm outdated` |
| `cache [command]` | Manage cache | `dpm cache info` |
| `pin <pkg>@<version>` | Pin package to exact version | `dpm pin requests@2.32.5` |
| `unpin <pkg>` | Unpin package (allow version ranges) | `dpm unpin requests` |
| `export <format> [output]` | Export dependencies | `dpm export requirements.txt` |
| `venv [command]` | Manage virtual environment | `dpm venv create` |
| `repo [command]` | Manage custom repositories | `dpm repo list` |

## Global Options

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show usage information |
| `--version` | Show version |
| `--verbose`, `-v` | Show detailed output |
| `--debug`, `-d` | Show debug information (includes verbose) |
| `--offline` | Use cache only, no network requests |
| `--skip-integrity` | Skip integrity verification |
| `--show-resolution` | Show detailed resolution steps |

## Command Details

### install

Install packages and their dependencies. If no packages are specified and `dpm.lock` exists, installs from the lock file.

```bash
# install specific packages
dpm install requests flask

# install from lock file
dpm install
```

### update

Update packages to their latest compatible versions.

```bash
# update all packages
dpm update

# update specific packages
dpm update requests numpy
```

### remove

Remove installed packages.

```bash
dpm remove flask django
```

### list

List all installed packages with versions.

```bash
dpm list
```

### resolve

Show what would be installed without actually installing (dry run).

```bash
dpm resolve flask django
```

### tree

Display dependency tree for packages.

```bash
dpm tree requests
dpm tree flask django
```

### lock

Generate a lock file without installing packages.

```bash
dpm lock requests flask
```

### search

Search for packages across all sources.

```bash
dpm search flask
dpm search json
```

### info

Show detailed information about a package.

```bash
dpm info requests
dpm info numpy
```

### init

Initialize a new `dpm.json` manifest file.

```bash
dpm init myproject 1.0.0
```

### clean

Remove packages that are not in `dpm.json` or `dpm.lock`.

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### outdated

Check for outdated packages.

```bash
dpm outdated
```

### cache

Manage the cache.

```bash
# show cache information
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### pin

Pin a package to an exact version in `dpm.json`.

```bash
dpm pin requests@2.32.5
```

### unpin

Unpin a package, allowing version ranges.

```bash
dpm unpin requests
```

### export

Export dependencies to other formats.

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json

# export lock file
dpm export lock
```

### venv

Manage virtual environments.

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
dpm venv use poetry

# remove venv
dpm venv remove
```

### repo

Manage custom package repositories. This feature allows you to configure additional package sources beyond the default ones (PyPI, npm, system).

**Status**: ✅ Fully implemented and tested. Custom repositories are used during package resolution.

**Security Note**: Credentials are stored in `~/.dpm/repositories.json` with restricted file permissions (600). However, passwords are stored in plain text. For better security:
- Use API tokens instead of passwords when possible
- Ensure the repositories file has proper permissions (`chmod 600 ~/.dpm/repositories.json`)
- Avoid committing this file to version control
- Consider using environment variables for sensitive credentials

**Use Cases:**

1. **Private Package Registries**: Add your company's internal package registry
   ```bash
   # Add private PyPI mirror
   dpm repo add company-pypi https://pypi.company.com
   
   # Add private npm registry with authentication (recommended: use token)
   dpm repo add company-npm https://npm.company.com token ""
   
   # Alternative: username/password (stored in plain text)
   dpm repo add company-npm https://npm.company.com username password
   ```

2. **Custom Package Sources**: Configure alternative package sources
   ```bash
   # Add a custom package repository
   dpm repo add custom https://packages.example.com
   ```

3. **Mirror Repositories**: Use faster or local mirrors
   ```bash
   # Add a local PyPI mirror
   dpm repo add local-pypi http://localhost:8080
   ```

**Commands:**

```bash
# list all configured repositories
dpm repo list

# add a repository (public)
dpm repo add myrepo https://example.com/repo

# add a repository with authentication (recommended: use token)
dpm repo add private https://private.com/repo token ""

# add a repository with username/password (stored in plain text)
dpm repo add private https://private.com/repo username password

# remove a repository
dpm repo remove myrepo
```

**How it works:**

Repositories are stored in `~/.dpm/repositories.json`:
```json
{
  "repositories": {
    "myrepo": {
      "url": "https://example.com/repo",
      "auth": null
    },
    "private": {
      "url": "https://private.com/repo",
      "auth": {
        "username": "user",
        "password": "pass"
      }
    }
  }
}
```

**How It Works:**

- Custom repositories are automatically checked during package resolution
- Authentication is handled automatically for authenticated repositories
- Repositories are checked after default sources (PyPI, npm, system)
- Supports both PyPI and npm repository formats
- Repository type is auto-detected from URL

## Examples

```bash
# install Python packages
dpm install numpy pandas matplotlib

# install npm packages
dpm install express lodash

# preview what would be installed
dpm resolve flask django

# show dependency tree
dpm tree requests

# search for packages
dpm search json

# create lock file
dpm lock requests flask

# install from lock file
dpm install

# check for outdated packages
dpm outdated

# update packages
dpm update

# export to requirements.txt
dpm export requirements.txt

# pin a package version
dpm pin requests@2.32.5

# create virtual environment
dpm venv create myenv

# add custom repository
dpm repo add myrepo https://example.com/repo
```

## Lock Files

Running `dpm lock` or `dpm install` generates a `dpm.lock` file in the current directory. This file pins exact versions for reproducible installs.

```bash
# create lock file
dpm lock requests flask

# install from lock file
dpm install
```

## Virtual Environments

DPM can create isolated environments to avoid polluting global installs:

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
```

The venv includes both Python (via `python3 -m venv`) and supports detection of conda, poetry, and pipenv environments.

## Integrity Verification

DPM verifies package integrity using SHA256 checksums. When packages are downloaded, their hashes are checked against the registry-provided integrity strings. This prevents tampered or corrupted packages from being installed.

After installation, DPM also verifies that:
- Python packages are importable
- npm packages exist in node_modules
- Installation was successful

If verification fails, DPM automatically rolls back the installation.

Use `--skip-integrity` to bypass verification (not recommended).

## Offline Mode

Use `--offline` to work without network access:

```bash
# resolve using only cached data
dpm --offline resolve requests
```

## Verbose/Debug Mode

Use `--verbose` or `--debug` for detailed output:

```bash
# verbose output
dpm --verbose resolve requests

# debug output (includes verbose)
dpm --debug resolve requests
```

## Resolution Details

Use `--show-resolution` to see detailed resolution steps:

```bash
dpm --show-resolution resolve flask django
```

This shows:
- Which algorithm was used (greedy vs backtracking)
- Number of packages resolved
- Conflicts detected (if any)
- Resolution time
- Timeout status (if applicable)

## Robustness Features

DPM includes several robustness features that work automatically:

### Network Resilience
- Automatic retry with exponential backoff (3 attempts by default)
- Timeout protection (30s per request)
- Rate limit handling (429 responses)
- Comprehensive error logging

### Input Validation
- Package names are sanitized to prevent path traversal attacks
- Version strings are validated
- Invalid inputs are rejected with clear error messages

### Cache Management
- Cache entries expire after 24 hours (TTL)
- Cache size is limited to 100MB (automatic eviction)
- Cache writes are atomic (no corruption on failures)

### Resolution Safety
- Resolution timeout (60s default) prevents infinite hangs
- Detailed conflict reporting when resolution fails
- Automatic rollback on installation failures

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `install <packages...>` | Install packages and their dependencies | `dpm install numpy pandas` |
| `update <packages...>` | Update packages to latest compatible versions | `dpm update requests` |
| `remove <packages...>` | Remove installed packages | `dpm remove flask` |
| `list` | List all installed packages | `dpm list` |
| `resolve <packages...>` | Show resolution plan without installing (dry run) | `dpm resolve django` |
| `tree <packages...>` | Display dependency tree | `dpm tree flask` |
| `lock <packages...>` | Generate lock file without installing | `dpm lock requests flask` |
| `search <query>` | Search for packages | `dpm search flask` |
| `info <package>` | Show package details | `dpm info requests` |
| `init [name] [version]` | Initialize dpm.json manifest file | `dpm init myproject 1.0.0` |
| `clean [--dry-run]` | Remove unused packages | `dpm clean` |
| `outdated` | Check for outdated packages | `dpm outdated` |
| `cache [command]` | Manage cache | `dpm cache info` |
| `pin <pkg>@<version>` | Pin package to exact version | `dpm pin requests@2.32.5` |
| `unpin <pkg>` | Unpin package (allow version ranges) | `dpm unpin requests` |
| `export <format> [output]` | Export dependencies | `dpm export requirements.txt` |
| `venv [command]` | Manage virtual environment | `dpm venv create` |
| `repo [command]` | Manage custom repositories | `dpm repo list` |

## Global Options

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show usage information |
| `--version` | Show version |
| `--verbose`, `-v` | Show detailed output |
| `--debug`, `-d` | Show debug information (includes verbose) |
| `--offline` | Use cache only, no network requests |
| `--skip-integrity` | Skip integrity verification |
| `--show-resolution` | Show detailed resolution steps |

## Command Details

### install

Install packages and their dependencies. If no packages are specified and `dpm.lock` exists, installs from the lock file.

```bash
# install specific packages
dpm install requests flask

# install from lock file
dpm install
```

### update

Update packages to their latest compatible versions.

```bash
# update all packages
dpm update

# update specific packages
dpm update requests numpy
```

### remove

Remove installed packages.

```bash
dpm remove flask django
```

### list

List all installed packages with versions.

```bash
dpm list
```

### resolve

Show what would be installed without actually installing (dry run).

```bash
dpm resolve flask django
```

### tree

Display dependency tree for packages.

```bash
dpm tree requests
dpm tree flask django
```

### lock

Generate a lock file without installing packages.

```bash
dpm lock requests flask
```

### search

Search for packages across all sources.

```bash
dpm search flask
dpm search json
```

### info

Show detailed information about a package.

```bash
dpm info requests
dpm info numpy
```

### init

Initialize a new `dpm.json` manifest file.

```bash
dpm init myproject 1.0.0
```

### clean

Remove packages that are not in `dpm.json` or `dpm.lock`.

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### outdated

Check for outdated packages.

```bash
dpm outdated
```

### cache

Manage the cache.

```bash
# show cache information
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### pin

Pin a package to an exact version in `dpm.json`.

```bash
dpm pin requests@2.32.5
```

### unpin

Unpin a package, allowing version ranges.

```bash
dpm unpin requests
```

### export

Export dependencies to other formats.

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json

# export lock file
dpm export lock
```

### venv

Manage virtual environments.

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
dpm venv use poetry

# remove venv
dpm venv remove
```

### repo

Manage custom package repositories. This feature allows you to configure additional package sources beyond the default ones (PyPI, npm, system).

**Status**: ✅ Fully implemented and tested. Custom repositories are used during package resolution.

**Security Note**: Credentials are stored in `~/.dpm/repositories.json` with restricted file permissions (600). However, passwords are stored in plain text. For better security:
- Use API tokens instead of passwords when possible
- Ensure the repositories file has proper permissions (`chmod 600 ~/.dpm/repositories.json`)
- Avoid committing this file to version control
- Consider using environment variables for sensitive credentials

**Use Cases:**

1. **Private Package Registries**: Add your company's internal package registry
   ```bash
   # Add private PyPI mirror
   dpm repo add company-pypi https://pypi.company.com
   
   # Add private npm registry with authentication (recommended: use token)
   dpm repo add company-npm https://npm.company.com token ""
   
   # Alternative: username/password (stored in plain text)
   dpm repo add company-npm https://npm.company.com username password
   ```

2. **Custom Package Sources**: Configure alternative package sources
   ```bash
   # Add a custom package repository
   dpm repo add custom https://packages.example.com
   ```

3. **Mirror Repositories**: Use faster or local mirrors
   ```bash
   # Add a local PyPI mirror
   dpm repo add local-pypi http://localhost:8080
   ```

**Commands:**

```bash
# list all configured repositories
dpm repo list

# add a repository (public)
dpm repo add myrepo https://example.com/repo

# add a repository with authentication (recommended: use token)
dpm repo add private https://private.com/repo token ""

# add a repository with username/password (stored in plain text)
dpm repo add private https://private.com/repo username password

# remove a repository
dpm repo remove myrepo
```

**How it works:**

Repositories are stored in `~/.dpm/repositories.json`:
```json
{
  "repositories": {
    "myrepo": {
      "url": "https://example.com/repo",
      "auth": null
    },
    "private": {
      "url": "https://private.com/repo",
      "auth": {
        "username": "user",
        "password": "pass"
      }
    }
  }
}
```

**How It Works:**

- Custom repositories are automatically checked during package resolution
- Authentication is handled automatically for authenticated repositories
- Repositories are checked after default sources (PyPI, npm, system)
- Supports both PyPI and npm repository formats
- Repository type is auto-detected from URL

## Examples

```bash
# install Python packages
dpm install numpy pandas matplotlib

# install npm packages
dpm install express lodash

# preview what would be installed
dpm resolve flask django

# show dependency tree
dpm tree requests

# search for packages
dpm search json

# create lock file
dpm lock requests flask

# install from lock file
dpm install

# check for outdated packages
dpm outdated

# update packages
dpm update

# export to requirements.txt
dpm export requirements.txt

# pin a package version
dpm pin requests@2.32.5

# create virtual environment
dpm venv create myenv

# add custom repository
dpm repo add myrepo https://example.com/repo
```

## Lock Files

Running `dpm lock` or `dpm install` generates a `dpm.lock` file in the current directory. This file pins exact versions for reproducible installs.

```bash
# create lock file
dpm lock requests flask

# install from lock file
dpm install
```

## Virtual Environments

DPM can create isolated environments to avoid polluting global installs:

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
```

The venv includes both Python (via `python3 -m venv`) and supports detection of conda, poetry, and pipenv environments.

## Integrity Verification

DPM verifies package integrity using SHA256 checksums. When packages are downloaded, their hashes are checked against the registry-provided integrity strings. This prevents tampered or corrupted packages from being installed.

After installation, DPM also verifies that:
- Python packages are importable
- npm packages exist in node_modules
- Installation was successful

If verification fails, DPM automatically rolls back the installation.

Use `--skip-integrity` to bypass verification (not recommended).

## Offline Mode

Use `--offline` to work without network access:

```bash
# resolve using only cached data
dpm --offline resolve requests
```

## Verbose/Debug Mode

Use `--verbose` or `--debug` for detailed output:

```bash
# verbose output
dpm --verbose resolve requests

# debug output (includes verbose)
dpm --debug resolve requests
```

## Resolution Details

Use `--show-resolution` to see detailed resolution steps:

```bash
dpm --show-resolution resolve flask django
```

This shows:
- Which algorithm was used (greedy vs backtracking)
- Number of packages resolved
- Conflicts detected (if any)
- Resolution time
- Timeout status (if applicable)

## Robustness Features

DPM includes several robustness features that work automatically:

### Network Resilience
- Automatic retry with exponential backoff (3 attempts by default)
- Timeout protection (30s per request)
- Rate limit handling (429 responses)
- Comprehensive error logging

### Input Validation
- Package names are sanitized to prevent path traversal attacks
- Version strings are validated
- Invalid inputs are rejected with clear error messages

### Cache Management
- Cache entries expire after 24 hours (TTL)
- Cache size is limited to 100MB (automatic eviction)
- Cache writes are atomic (no corruption on failures)

### Resolution Safety
- Resolution timeout (60s default) prevents infinite hangs
- Detailed conflict reporting when resolution fails
- Automatic rollback on installation failures

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `install <packages...>` | Install packages and their dependencies | `dpm install numpy pandas` |
| `update <packages...>` | Update packages to latest compatible versions | `dpm update requests` |
| `remove <packages...>` | Remove installed packages | `dpm remove flask` |
| `list` | List all installed packages | `dpm list` |
| `resolve <packages...>` | Show resolution plan without installing (dry run) | `dpm resolve django` |
| `tree <packages...>` | Display dependency tree | `dpm tree flask` |
| `lock <packages...>` | Generate lock file without installing | `dpm lock requests flask` |
| `search <query>` | Search for packages | `dpm search flask` |
| `info <package>` | Show package details | `dpm info requests` |
| `init [name] [version]` | Initialize dpm.json manifest file | `dpm init myproject 1.0.0` |
| `clean [--dry-run]` | Remove unused packages | `dpm clean` |
| `outdated` | Check for outdated packages | `dpm outdated` |
| `cache [command]` | Manage cache | `dpm cache info` |
| `pin <pkg>@<version>` | Pin package to exact version | `dpm pin requests@2.32.5` |
| `unpin <pkg>` | Unpin package (allow version ranges) | `dpm unpin requests` |
| `export <format> [output]` | Export dependencies | `dpm export requirements.txt` |
| `venv [command]` | Manage virtual environment | `dpm venv create` |
| `repo [command]` | Manage custom repositories | `dpm repo list` |

## Global Options

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show usage information |
| `--version` | Show version |
| `--verbose`, `-v` | Show detailed output |
| `--debug`, `-d` | Show debug information (includes verbose) |
| `--offline` | Use cache only, no network requests |
| `--skip-integrity` | Skip integrity verification |
| `--show-resolution` | Show detailed resolution steps |

## Command Details

### install

Install packages and their dependencies. If no packages are specified and `dpm.lock` exists, installs from the lock file.

```bash
# install specific packages
dpm install requests flask

# install from lock file
dpm install
```

### update

Update packages to their latest compatible versions.

```bash
# update all packages
dpm update

# update specific packages
dpm update requests numpy
```

### remove

Remove installed packages.

```bash
dpm remove flask django
```

### list

List all installed packages with versions.

```bash
dpm list
```

### resolve

Show what would be installed without actually installing (dry run).

```bash
dpm resolve flask django
```

### tree

Display dependency tree for packages.

```bash
dpm tree requests
dpm tree flask django
```

### lock

Generate a lock file without installing packages.

```bash
dpm lock requests flask
```

### search

Search for packages across all sources.

```bash
dpm search flask
dpm search json
```

### info

Show detailed information about a package.

```bash
dpm info requests
dpm info numpy
```

### init

Initialize a new `dpm.json` manifest file.

```bash
dpm init myproject 1.0.0
```

### clean

Remove packages that are not in `dpm.json` or `dpm.lock`.

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### outdated

Check for outdated packages.

```bash
dpm outdated
```

### cache

Manage the cache.

```bash
# show cache information
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### pin

Pin a package to an exact version in `dpm.json`.

```bash
dpm pin requests@2.32.5
```

### unpin

Unpin a package, allowing version ranges.

```bash
dpm unpin requests
```

### export

Export dependencies to other formats.

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json

# export lock file
dpm export lock
```

### venv

Manage virtual environments.

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
dpm venv use poetry

# remove venv
dpm venv remove
```

### repo

Manage custom package repositories. This feature allows you to configure additional package sources beyond the default ones (PyPI, npm, system).

**Status**: ✅ Fully implemented and tested. Custom repositories are used during package resolution.

**Security Note**: Credentials are stored in `~/.dpm/repositories.json` with restricted file permissions (600). However, passwords are stored in plain text. For better security:
- Use API tokens instead of passwords when possible
- Ensure the repositories file has proper permissions (`chmod 600 ~/.dpm/repositories.json`)
- Avoid committing this file to version control
- Consider using environment variables for sensitive credentials

**Use Cases:**

1. **Private Package Registries**: Add your company's internal package registry
   ```bash
   # Add private PyPI mirror
   dpm repo add company-pypi https://pypi.company.com
   
   # Add private npm registry with authentication (recommended: use token)
   dpm repo add company-npm https://npm.company.com token ""
   
   # Alternative: username/password (stored in plain text)
   dpm repo add company-npm https://npm.company.com username password
   ```

2. **Custom Package Sources**: Configure alternative package sources
   ```bash
   # Add a custom package repository
   dpm repo add custom https://packages.example.com
   ```

3. **Mirror Repositories**: Use faster or local mirrors
   ```bash
   # Add a local PyPI mirror
   dpm repo add local-pypi http://localhost:8080
   ```

**Commands:**

```bash
# list all configured repositories
dpm repo list

# add a repository (public)
dpm repo add myrepo https://example.com/repo

# add a repository with authentication (recommended: use token)
dpm repo add private https://private.com/repo token ""

# add a repository with username/password (stored in plain text)
dpm repo add private https://private.com/repo username password

# remove a repository
dpm repo remove myrepo
```

**How it works:**

Repositories are stored in `~/.dpm/repositories.json`:
```json
{
  "repositories": {
    "myrepo": {
      "url": "https://example.com/repo",
      "auth": null
    },
    "private": {
      "url": "https://private.com/repo",
      "auth": {
        "username": "user",
        "password": "pass"
      }
    }
  }
}
```

**How It Works:**

- Custom repositories are automatically checked during package resolution
- Authentication is handled automatically for authenticated repositories
- Repositories are checked after default sources (PyPI, npm, system)
- Supports both PyPI and npm repository formats
- Repository type is auto-detected from URL

## Examples

```bash
# install Python packages
dpm install numpy pandas matplotlib

# install npm packages
dpm install express lodash

# preview what would be installed
dpm resolve flask django

# show dependency tree
dpm tree requests

# search for packages
dpm search json

# create lock file
dpm lock requests flask

# install from lock file
dpm install

# check for outdated packages
dpm outdated

# update packages
dpm update

# export to requirements.txt
dpm export requirements.txt

# pin a package version
dpm pin requests@2.32.5

# create virtual environment
dpm venv create myenv

# add custom repository
dpm repo add myrepo https://example.com/repo
```

## Lock Files

Running `dpm lock` or `dpm install` generates a `dpm.lock` file in the current directory. This file pins exact versions for reproducible installs.

```bash
# create lock file
dpm lock requests flask

# install from lock file
dpm install
```

## Virtual Environments

DPM can create isolated environments to avoid polluting global installs:

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
```

The venv includes both Python (via `python3 -m venv`) and supports detection of conda, poetry, and pipenv environments.

## Integrity Verification

DPM verifies package integrity using SHA256 checksums. When packages are downloaded, their hashes are checked against the registry-provided integrity strings. This prevents tampered or corrupted packages from being installed.

After installation, DPM also verifies that:
- Python packages are importable
- npm packages exist in node_modules
- Installation was successful

If verification fails, DPM automatically rolls back the installation.

Use `--skip-integrity` to bypass verification (not recommended).

## Offline Mode

Use `--offline` to work without network access:

```bash
# resolve using only cached data
dpm --offline resolve requests
```

## Verbose/Debug Mode

Use `--verbose` or `--debug` for detailed output:

```bash
# verbose output
dpm --verbose resolve requests

# debug output (includes verbose)
dpm --debug resolve requests
```

## Resolution Details

Use `--show-resolution` to see detailed resolution steps:

```bash
dpm --show-resolution resolve flask django
```

This shows:
- Which algorithm was used (greedy vs backtracking)
- Number of packages resolved
- Conflicts detected (if any)
- Resolution time
- Timeout status (if applicable)

## Robustness Features

DPM includes several robustness features that work automatically:

### Network Resilience
- Automatic retry with exponential backoff (3 attempts by default)
- Timeout protection (30s per request)
- Rate limit handling (429 responses)
- Comprehensive error logging

### Input Validation
- Package names are sanitized to prevent path traversal attacks
- Version strings are validated
- Invalid inputs are rejected with clear error messages

### Cache Management
- Cache entries expire after 24 hours (TTL)
- Cache size is limited to 100MB (automatic eviction)
- Cache writes are atomic (no corruption on failures)

### Resolution Safety
- Resolution timeout (60s default) prevents infinite hangs
- Detailed conflict reporting when resolution fails
- Automatic rollback on installation failures

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `install <packages...>` | Install packages and their dependencies | `dpm install numpy pandas` |
| `update <packages...>` | Update packages to latest compatible versions | `dpm update requests` |
| `remove <packages...>` | Remove installed packages | `dpm remove flask` |
| `list` | List all installed packages | `dpm list` |
| `resolve <packages...>` | Show resolution plan without installing (dry run) | `dpm resolve django` |
| `tree <packages...>` | Display dependency tree | `dpm tree flask` |
| `lock <packages...>` | Generate lock file without installing | `dpm lock requests flask` |
| `search <query>` | Search for packages | `dpm search flask` |
| `info <package>` | Show package details | `dpm info requests` |
| `init [name] [version]` | Initialize dpm.json manifest file | `dpm init myproject 1.0.0` |
| `clean [--dry-run]` | Remove unused packages | `dpm clean` |
| `outdated` | Check for outdated packages | `dpm outdated` |
| `cache [command]` | Manage cache | `dpm cache info` |
| `pin <pkg>@<version>` | Pin package to exact version | `dpm pin requests@2.32.5` |
| `unpin <pkg>` | Unpin package (allow version ranges) | `dpm unpin requests` |
| `export <format> [output]` | Export dependencies | `dpm export requirements.txt` |
| `venv [command]` | Manage virtual environment | `dpm venv create` |
| `repo [command]` | Manage custom repositories | `dpm repo list` |

## Global Options

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show usage information |
| `--version` | Show version |
| `--verbose`, `-v` | Show detailed output |
| `--debug`, `-d` | Show debug information (includes verbose) |
| `--offline` | Use cache only, no network requests |
| `--skip-integrity` | Skip integrity verification |
| `--show-resolution` | Show detailed resolution steps |

## Command Details

### install

Install packages and their dependencies. If no packages are specified and `dpm.lock` exists, installs from the lock file.

```bash
# install specific packages
dpm install requests flask

# install from lock file
dpm install
```

### update

Update packages to their latest compatible versions.

```bash
# update all packages
dpm update

# update specific packages
dpm update requests numpy
```

### remove

Remove installed packages.

```bash
dpm remove flask django
```

### list

List all installed packages with versions.

```bash
dpm list
```

### resolve

Show what would be installed without actually installing (dry run).

```bash
dpm resolve flask django
```

### tree

Display dependency tree for packages.

```bash
dpm tree requests
dpm tree flask django
```

### lock

Generate a lock file without installing packages.

```bash
dpm lock requests flask
```

### search

Search for packages across all sources.

```bash
dpm search flask
dpm search json
```

### info

Show detailed information about a package.

```bash
dpm info requests
dpm info numpy
```

### init

Initialize a new `dpm.json` manifest file.

```bash
dpm init myproject 1.0.0
```

### clean

Remove packages that are not in `dpm.json` or `dpm.lock`.

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### outdated

Check for outdated packages.

```bash
dpm outdated
```

### cache

Manage the cache.

```bash
# show cache information
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### pin

Pin a package to an exact version in `dpm.json`.

```bash
dpm pin requests@2.32.5
```

### unpin

Unpin a package, allowing version ranges.

```bash
dpm unpin requests
```

### export

Export dependencies to other formats.

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json

# export lock file
dpm export lock
```

### venv

Manage virtual environments.

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
dpm venv use poetry

# remove venv
dpm venv remove
```

### repo

Manage custom package repositories. This feature allows you to configure additional package sources beyond the default ones (PyPI, npm, system).

**Status**: ✅ Fully implemented and tested. Custom repositories are used during package resolution.

**Security Note**: Credentials are stored in `~/.dpm/repositories.json` with restricted file permissions (600). However, passwords are stored in plain text. For better security:
- Use API tokens instead of passwords when possible
- Ensure the repositories file has proper permissions (`chmod 600 ~/.dpm/repositories.json`)
- Avoid committing this file to version control
- Consider using environment variables for sensitive credentials

**Use Cases:**

1. **Private Package Registries**: Add your company's internal package registry
   ```bash
   # Add private PyPI mirror
   dpm repo add company-pypi https://pypi.company.com
   
   # Add private npm registry with authentication (recommended: use token)
   dpm repo add company-npm https://npm.company.com token ""
   
   # Alternative: username/password (stored in plain text)
   dpm repo add company-npm https://npm.company.com username password
   ```

2. **Custom Package Sources**: Configure alternative package sources
   ```bash
   # Add a custom package repository
   dpm repo add custom https://packages.example.com
   ```

3. **Mirror Repositories**: Use faster or local mirrors
   ```bash
   # Add a local PyPI mirror
   dpm repo add local-pypi http://localhost:8080
   ```

**Commands:**

```bash
# list all configured repositories
dpm repo list

# add a repository (public)
dpm repo add myrepo https://example.com/repo

# add a repository with authentication (recommended: use token)
dpm repo add private https://private.com/repo token ""

# add a repository with username/password (stored in plain text)
dpm repo add private https://private.com/repo username password

# remove a repository
dpm repo remove myrepo
```

**How it works:**

Repositories are stored in `~/.dpm/repositories.json`:
```json
{
  "repositories": {
    "myrepo": {
      "url": "https://example.com/repo",
      "auth": null
    },
    "private": {
      "url": "https://private.com/repo",
      "auth": {
        "username": "user",
        "password": "pass"
      }
    }
  }
}
```

**How It Works:**

- Custom repositories are automatically checked during package resolution
- Authentication is handled automatically for authenticated repositories
- Repositories are checked after default sources (PyPI, npm, system)
- Supports both PyPI and npm repository formats
- Repository type is auto-detected from URL

## Examples

```bash
# install Python packages
dpm install numpy pandas matplotlib

# install npm packages
dpm install express lodash

# preview what would be installed
dpm resolve flask django

# show dependency tree
dpm tree requests

# search for packages
dpm search json

# create lock file
dpm lock requests flask

# install from lock file
dpm install

# check for outdated packages
dpm outdated

# update packages
dpm update

# export to requirements.txt
dpm export requirements.txt

# pin a package version
dpm pin requests@2.32.5

# create virtual environment
dpm venv create myenv

# add custom repository
dpm repo add myrepo https://example.com/repo
```

## Lock Files

Running `dpm lock` or `dpm install` generates a `dpm.lock` file in the current directory. This file pins exact versions for reproducible installs.

```bash
# create lock file
dpm lock requests flask

# install from lock file
dpm install
```

## Virtual Environments

DPM can create isolated environments to avoid polluting global installs:

```bash
# create a venv
dpm venv create myenv

# check status
dpm venv status

# detect existing environments
dpm venv detect

# use existing environment
dpm venv use conda
```

The venv includes both Python (via `python3 -m venv`) and supports detection of conda, poetry, and pipenv environments.

## Integrity Verification

DPM verifies package integrity using SHA256 checksums. When packages are downloaded, their hashes are checked against the registry-provided integrity strings. This prevents tampered or corrupted packages from being installed.

After installation, DPM also verifies that:
- Python packages are importable
- npm packages exist in node_modules
- Installation was successful

If verification fails, DPM automatically rolls back the installation.

Use `--skip-integrity` to bypass verification (not recommended).

## Offline Mode

Use `--offline` to work without network access:

```bash
# resolve using only cached data
dpm --offline resolve requests
```

## Verbose/Debug Mode

Use `--verbose` or `--debug` for detailed output:

```bash
# verbose output
dpm --verbose resolve requests

# debug output (includes verbose)
dpm --debug resolve requests
```

## Resolution Details

Use `--show-resolution` to see detailed resolution steps:

```bash
dpm --show-resolution resolve flask django
```

This shows:
- Which algorithm was used (greedy vs backtracking)
- Number of packages resolved
- Conflicts detected (if any)
- Resolution time
- Timeout status (if applicable)

## Robustness Features

DPM includes several robustness features that work automatically:

### Network Resilience
- Automatic retry with exponential backoff (3 attempts by default)
- Timeout protection (30s per request)
- Rate limit handling (429 responses)
- Comprehensive error logging

### Input Validation
- Package names are sanitized to prevent path traversal attacks
- Version strings are validated
- Invalid inputs are rejected with clear error messages

### Cache Management
- Cache entries expire after 24 hours (TTL)
- Cache size is limited to 100MB (automatic eviction)
- Cache writes are atomic (no corruption on failures)

### Resolution Safety
- Resolution timeout (60s default) prevents infinite hangs
- Detailed conflict reporting when resolution fails
- Automatic rollback on installation failures
