# Architecture

DPM is organized into several modules:

```
dpm/
├── core/              # Data structures and utilities
├── resolver/          # Dependency resolution algorithms
├── sources/           # Package registry integrations
├── installer/         # Installation, venv, integrity checking
├── network/           # HTTP client and caching
└── cli/               # Command handlers
```

## Resolution Flow

1. User requests packages via CLI
2. `CommandHandler` parses input and initializes sources
3. `DependencyResolver` attempts resolution:
   - Tries `GreedyResolver` first (fast path)
   - Falls back to `BacktrackResolver` if conflicts found
4. Resolution result contains selected versions for all packages
5. `InstallationPlan` orders packages by dependencies
6. `Installer` executes the plan in dependency order

## Key Components

### DependencyResolver

The hybrid resolver (`resolver/resolver.py`) coordinates between greedy and backtracking approaches. It returns a `ResolutionResult`:

```python
@dataclass
class ResolutionResult:
    success: bool
    selected_versions: Dict[str, str]  # package -> version
    error_message: Optional[str]
    used_backtracking: bool
    conflict_details: Dict[str, List[str]]
    dependency_graph: Optional[object]
```

### Version Constraints

Supported constraint operators (`core/version.py`):
- `==`, `!=`, `<`, `<=`, `>`, `>=`
- `~` (tilde): allows patch updates (`~1.2.3` = `>=1.2.3,<1.3.0`)
- `^` (caret): allows minor updates (`^1.2.3` = `>=1.2.3,<2.0.0`)

Multiple constraints can be combined: `>=1.0.0,<2.0.0`

### Sources

Each source implements the `Source` interface:
- `fetch_latest(package_name)` - returns latest version
- `fetch_version(package_name, version)` - returns specific version
- `get_dependencies(package_name, version)` - returns dependencies
- `package_exists(package_name)` - checks if package exists
- `search(query, limit)` - searches for packages
- `prefetch(names)` - prefetches multiple packages in parallel

Current implementations: PyPI, npm, system (apt/yum/brew), local JSON files.

### Manifest (dpm.json)

The `Manifest` class (`core/manifest.py`) handles project configuration:

```json
{
  "name": "project-name",
  "version": "1.0.0",
  "dependencies": {
    "requests": "^2.32.0"
  },
  "devDependencies": {},
  "sources": ["pypi", "npm"]
}
```

### Lock File (dpm.lock)

The `LockFile` class (`installer/lockfile.py`) manages reproducible builds:

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

## Caching

HTTP responses are cached in `~/.dpm/cache/` to avoid repeated network requests. The `Cache` class (`network/cache.py`) uses file-based caching with SHA256 hashing of URLs.

**Features:**
- **TTL (Time To Live)**: Cache entries expire after 24 hours by default
- **Size Limits**: Cache automatically evicts oldest entries when size exceeds 100MB
- **Atomic Writes**: Cache writes use temporary files and atomic moves to prevent corruption
- **Memory Cache**: Frequently accessed entries are cached in memory for faster access

Cache management:
- `dpm cache info` - show cache size and location
- `dpm cache list` - list cached entries
- `dpm cache clear` - clear all cached data

## Virtual Environments

`VirtualEnv` (`installer/venv.py`) manages isolated environments:
- Creates Python venv via `python3 -m venv`
- Detects existing environments (conda, poetry, pipenv)
- Handles activation scripts

## Integrity Verification

`Installer` (`installer/installer.py`) handles package verification:
- Computes SHA256 hashes of downloaded packages
- Verifies against registry-provided integrity strings
- Uses the `sha256-<hex>` format
- Verifies packages are importable after installation (Python) or exist (npm)
- Automatically rolls back installations on verification failure

## Installation Plan

`InstallationPlan` (`installer/plan.py`) orders packages by dependencies:
- Uses topological sort to determine installation order
- Groups packages that can be installed in parallel
- Ensures dependencies are installed before dependents

## Configuration

`Config` (`core/config.py`) manages user and project settings:
- User config: `~/.dpm/config.json`
- Project config: `dpm.config.json` (optional)
- Supports: cache_dir, default_sources, timeout, max_workers, log_level

## Logging

`Logger` (`core/logger.py`) provides structured logging:
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Console and file logging
- Configurable log levels

## Export/Import

`Exporter` (`core/exporter.py`) handles format conversion:
- Export to `requirements.txt` (pip format)
- Export to `package.json` (npm format)
- Export lock file

## Repository Management

`RepositoryManager` (`core/repository.py`) manages custom repositories:
- Add/remove custom package sources
- Support for authenticated repositories
- Stored in `~/.dpm/repositories.json`

## Robustness Features

### Network Resilience

`HttpClient` (`network/http_client.py`) includes:
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts by default)
- **Timeout Protection**: 30-second timeout per request
- **Error Handling**: Handles HTTP errors, URL errors, and network failures gracefully
- **Rate Limit Handling**: Special handling for 429 (Too Many Requests) responses

### Input Validation

`Validation` (`core/validation.py`) provides:
- **Package Name Sanitization**: Prevents path traversal attacks and invalid characters
- **Version Validation**: Ensures version strings are valid semantic versions
- **Constraint Validation**: Validates version constraint syntax

### File Safety

- **Atomic Writes**: Lock files and cache use temporary files and atomic moves
- **Error Recovery**: Failed writes don't corrupt existing files
- **Transaction Safety**: All-or-nothing file operations

### Performance Optimizations

- **SystemSource Caching**: System package existence checks are cached to avoid expensive subprocess calls
- **Heuristic Filtering**: SystemSource skips checking packages that are clearly Python/JS packages
- **Subprocess Timeouts**: System package checks have 2-second timeouts to prevent hangs
- **Cache Size Optimization**: Cache size checks are performed periodically, not on every write

### Resolution Safety

- **Timeout Protection**: Resolution has a 60-second timeout to prevent infinite hangs
- **Error Reporting**: Detailed conflict information when resolution fails
- **Rollback Support**: Failed installations are automatically rolled back

DPM is organized into several modules:

```
dpm/
├── core/              # Data structures and utilities
├── resolver/          # Dependency resolution algorithms
├── sources/           # Package registry integrations
├── installer/         # Installation, venv, integrity checking
├── network/           # HTTP client and caching
└── cli/               # Command handlers
```

## Resolution Flow

1. User requests packages via CLI
2. `CommandHandler` parses input and initializes sources
3. `DependencyResolver` attempts resolution:
   - Tries `GreedyResolver` first (fast path)
   - Falls back to `BacktrackResolver` if conflicts found
4. Resolution result contains selected versions for all packages
5. `InstallationPlan` orders packages by dependencies
6. `Installer` executes the plan in dependency order

## Key Components

### DependencyResolver

The hybrid resolver (`resolver/resolver.py`) coordinates between greedy and backtracking approaches. It returns a `ResolutionResult`:

```python
@dataclass
class ResolutionResult:
    success: bool
    selected_versions: Dict[str, str]  # package -> version
    error_message: Optional[str]
    used_backtracking: bool
    conflict_details: Dict[str, List[str]]
    dependency_graph: Optional[object]
```

### Version Constraints

Supported constraint operators (`core/version.py`):
- `==`, `!=`, `<`, `<=`, `>`, `>=`
- `~` (tilde): allows patch updates (`~1.2.3` = `>=1.2.3,<1.3.0`)
- `^` (caret): allows minor updates (`^1.2.3` = `>=1.2.3,<2.0.0`)

Multiple constraints can be combined: `>=1.0.0,<2.0.0`

### Sources

Each source implements the `Source` interface:
- `fetch_latest(package_name)` - returns latest version
- `fetch_version(package_name, version)` - returns specific version
- `get_dependencies(package_name, version)` - returns dependencies
- `package_exists(package_name)` - checks if package exists
- `search(query, limit)` - searches for packages
- `prefetch(names)` - prefetches multiple packages in parallel

Current implementations: PyPI, npm, system (apt/yum/brew), local JSON files.

### Manifest (dpm.json)

The `Manifest` class (`core/manifest.py`) handles project configuration:

```json
{
  "name": "project-name",
  "version": "1.0.0",
  "dependencies": {
    "requests": "^2.32.0"
  },
  "devDependencies": {},
  "sources": ["pypi", "npm"]
}
```

### Lock File (dpm.lock)

The `LockFile` class (`installer/lockfile.py`) manages reproducible builds:

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

## Caching

HTTP responses are cached in `~/.dpm/cache/` to avoid repeated network requests. The `Cache` class (`network/cache.py`) uses file-based caching with SHA256 hashing of URLs.

**Features:**
- **TTL (Time To Live)**: Cache entries expire after 24 hours by default
- **Size Limits**: Cache automatically evicts oldest entries when size exceeds 100MB
- **Atomic Writes**: Cache writes use temporary files and atomic moves to prevent corruption
- **Memory Cache**: Frequently accessed entries are cached in memory for faster access

Cache management:
- `dpm cache info` - show cache size and location
- `dpm cache list` - list cached entries
- `dpm cache clear` - clear all cached data

## Virtual Environments

`VirtualEnv` (`installer/venv.py`) manages isolated environments:
- Creates Python venv via `python3 -m venv`
- Detects existing environments (conda, poetry, pipenv)
- Handles activation scripts

## Integrity Verification

`Installer` (`installer/installer.py`) handles package verification:
- Computes SHA256 hashes of downloaded packages
- Verifies against registry-provided integrity strings
- Uses the `sha256-<hex>` format
- Verifies packages are importable after installation (Python) or exist (npm)
- Automatically rolls back installations on verification failure

## Installation Plan

`InstallationPlan` (`installer/plan.py`) orders packages by dependencies:
- Uses topological sort to determine installation order
- Groups packages that can be installed in parallel
- Ensures dependencies are installed before dependents

## Configuration

`Config` (`core/config.py`) manages user and project settings:
- User config: `~/.dpm/config.json`
- Project config: `dpm.config.json` (optional)
- Supports: cache_dir, default_sources, timeout, max_workers, log_level

## Logging

`Logger` (`core/logger.py`) provides structured logging:
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Console and file logging
- Configurable log levels

## Export/Import

`Exporter` (`core/exporter.py`) handles format conversion:
- Export to `requirements.txt` (pip format)
- Export to `package.json` (npm format)
- Export lock file

## Repository Management

`RepositoryManager` (`core/repository.py`) manages custom repositories:
- Add/remove custom package sources
- Support for authenticated repositories
- Stored in `~/.dpm/repositories.json`

## Robustness Features

### Network Resilience

`HttpClient` (`network/http_client.py`) includes:
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts by default)
- **Timeout Protection**: 30-second timeout per request
- **Error Handling**: Handles HTTP errors, URL errors, and network failures gracefully
- **Rate Limit Handling**: Special handling for 429 (Too Many Requests) responses

### Input Validation

`Validation` (`core/validation.py`) provides:
- **Package Name Sanitization**: Prevents path traversal attacks and invalid characters
- **Version Validation**: Ensures version strings are valid semantic versions
- **Constraint Validation**: Validates version constraint syntax

### File Safety

- **Atomic Writes**: Lock files and cache use temporary files and atomic moves
- **Error Recovery**: Failed writes don't corrupt existing files
- **Transaction Safety**: All-or-nothing file operations

### Performance Optimizations

- **SystemSource Caching**: System package existence checks are cached to avoid expensive subprocess calls
- **Heuristic Filtering**: SystemSource skips checking packages that are clearly Python/JS packages
- **Subprocess Timeouts**: System package checks have 2-second timeouts to prevent hangs
- **Cache Size Optimization**: Cache size checks are performed periodically, not on every write

### Resolution Safety

- **Timeout Protection**: Resolution has a 60-second timeout to prevent infinite hangs
- **Error Reporting**: Detailed conflict information when resolution fails
- **Rollback Support**: Failed installations are automatically rolled back

DPM is organized into several modules:

```
dpm/
├── core/              # Data structures and utilities
├── resolver/          # Dependency resolution algorithms
├── sources/           # Package registry integrations
├── installer/         # Installation, venv, integrity checking
├── network/           # HTTP client and caching
└── cli/               # Command handlers
```

## Resolution Flow

1. User requests packages via CLI
2. `CommandHandler` parses input and initializes sources
3. `DependencyResolver` attempts resolution:
   - Tries `GreedyResolver` first (fast path)
   - Falls back to `BacktrackResolver` if conflicts found
4. Resolution result contains selected versions for all packages
5. `InstallationPlan` orders packages by dependencies
6. `Installer` executes the plan in dependency order

## Key Components

### DependencyResolver

The hybrid resolver (`resolver/resolver.py`) coordinates between greedy and backtracking approaches. It returns a `ResolutionResult`:

```python
@dataclass
class ResolutionResult:
    success: bool
    selected_versions: Dict[str, str]  # package -> version
    error_message: Optional[str]
    used_backtracking: bool
    conflict_details: Dict[str, List[str]]
    dependency_graph: Optional[object]
```

### Version Constraints

Supported constraint operators (`core/version.py`):
- `==`, `!=`, `<`, `<=`, `>`, `>=`
- `~` (tilde): allows patch updates (`~1.2.3` = `>=1.2.3,<1.3.0`)
- `^` (caret): allows minor updates (`^1.2.3` = `>=1.2.3,<2.0.0`)

Multiple constraints can be combined: `>=1.0.0,<2.0.0`

### Sources

Each source implements the `Source` interface:
- `fetch_latest(package_name)` - returns latest version
- `fetch_version(package_name, version)` - returns specific version
- `get_dependencies(package_name, version)` - returns dependencies
- `package_exists(package_name)` - checks if package exists
- `search(query, limit)` - searches for packages
- `prefetch(names)` - prefetches multiple packages in parallel

Current implementations: PyPI, npm, system (apt/yum/brew), local JSON files.

### Manifest (dpm.json)

The `Manifest` class (`core/manifest.py`) handles project configuration:

```json
{
  "name": "project-name",
  "version": "1.0.0",
  "dependencies": {
    "requests": "^2.32.0"
  },
  "devDependencies": {},
  "sources": ["pypi", "npm"]
}
```

### Lock File (dpm.lock)

The `LockFile` class (`installer/lockfile.py`) manages reproducible builds:

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

## Caching

HTTP responses are cached in `~/.dpm/cache/` to avoid repeated network requests. The `Cache` class (`network/cache.py`) uses file-based caching with SHA256 hashing of URLs.

**Features:**
- **TTL (Time To Live)**: Cache entries expire after 24 hours by default
- **Size Limits**: Cache automatically evicts oldest entries when size exceeds 100MB
- **Atomic Writes**: Cache writes use temporary files and atomic moves to prevent corruption
- **Memory Cache**: Frequently accessed entries are cached in memory for faster access

Cache management:
- `dpm cache info` - show cache size and location
- `dpm cache list` - list cached entries
- `dpm cache clear` - clear all cached data

## Virtual Environments

`VirtualEnv` (`installer/venv.py`) manages isolated environments:
- Creates Python venv via `python3 -m venv`
- Detects existing environments (conda, poetry, pipenv)
- Handles activation scripts

## Integrity Verification

`Installer` (`installer/installer.py`) handles package verification:
- Computes SHA256 hashes of downloaded packages
- Verifies against registry-provided integrity strings
- Uses the `sha256-<hex>` format
- Verifies packages are importable after installation (Python) or exist (npm)
- Automatically rolls back installations on verification failure

## Installation Plan

`InstallationPlan` (`installer/plan.py`) orders packages by dependencies:
- Uses topological sort to determine installation order
- Groups packages that can be installed in parallel
- Ensures dependencies are installed before dependents

## Configuration

`Config` (`core/config.py`) manages user and project settings:
- User config: `~/.dpm/config.json`
- Project config: `dpm.config.json` (optional)
- Supports: cache_dir, default_sources, timeout, max_workers, log_level

## Logging

`Logger` (`core/logger.py`) provides structured logging:
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Console and file logging
- Configurable log levels

## Export/Import

`Exporter` (`core/exporter.py`) handles format conversion:
- Export to `requirements.txt` (pip format)
- Export to `package.json` (npm format)
- Export lock file

## Repository Management

`RepositoryManager` (`core/repository.py`) manages custom repositories:
- Add/remove custom package sources
- Support for authenticated repositories
- Stored in `~/.dpm/repositories.json`

## Robustness Features

### Network Resilience

`HttpClient` (`network/http_client.py`) includes:
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts by default)
- **Timeout Protection**: 30-second timeout per request
- **Error Handling**: Handles HTTP errors, URL errors, and network failures gracefully
- **Rate Limit Handling**: Special handling for 429 (Too Many Requests) responses

### Input Validation

`Validation` (`core/validation.py`) provides:
- **Package Name Sanitization**: Prevents path traversal attacks and invalid characters
- **Version Validation**: Ensures version strings are valid semantic versions
- **Constraint Validation**: Validates version constraint syntax

### File Safety

- **Atomic Writes**: Lock files and cache use temporary files and atomic moves
- **Error Recovery**: Failed writes don't corrupt existing files
- **Transaction Safety**: All-or-nothing file operations

### Performance Optimizations

- **SystemSource Caching**: System package existence checks are cached to avoid expensive subprocess calls
- **Heuristic Filtering**: SystemSource skips checking packages that are clearly Python/JS packages
- **Subprocess Timeouts**: System package checks have 2-second timeouts to prevent hangs
- **Cache Size Optimization**: Cache size checks are performed periodically, not on every write

### Resolution Safety

- **Timeout Protection**: Resolution has a 60-second timeout to prevent infinite hangs
- **Error Reporting**: Detailed conflict information when resolution fails
- **Rollback Support**: Failed installations are automatically rolled back

DPM is organized into several modules:

```
dpm/
├── core/              # Data structures and utilities
├── resolver/          # Dependency resolution algorithms
├── sources/           # Package registry integrations
├── installer/         # Installation, venv, integrity checking
├── network/           # HTTP client and caching
└── cli/               # Command handlers
```

## Resolution Flow

1. User requests packages via CLI
2. `CommandHandler` parses input and initializes sources
3. `DependencyResolver` attempts resolution:
   - Tries `GreedyResolver` first (fast path)
   - Falls back to `BacktrackResolver` if conflicts found
4. Resolution result contains selected versions for all packages
5. `InstallationPlan` orders packages by dependencies
6. `Installer` executes the plan in dependency order

## Key Components

### DependencyResolver

The hybrid resolver (`resolver/resolver.py`) coordinates between greedy and backtracking approaches. It returns a `ResolutionResult`:

```python
@dataclass
class ResolutionResult:
    success: bool
    selected_versions: Dict[str, str]  # package -> version
    error_message: Optional[str]
    used_backtracking: bool
    conflict_details: Dict[str, List[str]]
    dependency_graph: Optional[object]
```

### Version Constraints

Supported constraint operators (`core/version.py`):
- `==`, `!=`, `<`, `<=`, `>`, `>=`
- `~` (tilde): allows patch updates (`~1.2.3` = `>=1.2.3,<1.3.0`)
- `^` (caret): allows minor updates (`^1.2.3` = `>=1.2.3,<2.0.0`)

Multiple constraints can be combined: `>=1.0.0,<2.0.0`

### Sources

Each source implements the `Source` interface:
- `fetch_latest(package_name)` - returns latest version
- `fetch_version(package_name, version)` - returns specific version
- `get_dependencies(package_name, version)` - returns dependencies
- `package_exists(package_name)` - checks if package exists
- `search(query, limit)` - searches for packages
- `prefetch(names)` - prefetches multiple packages in parallel

Current implementations: PyPI, npm, system (apt/yum/brew), local JSON files.

### Manifest (dpm.json)

The `Manifest` class (`core/manifest.py`) handles project configuration:

```json
{
  "name": "project-name",
  "version": "1.0.0",
  "dependencies": {
    "requests": "^2.32.0"
  },
  "devDependencies": {},
  "sources": ["pypi", "npm"]
}
```

### Lock File (dpm.lock)

The `LockFile` class (`installer/lockfile.py`) manages reproducible builds:

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

## Caching

HTTP responses are cached in `~/.dpm/cache/` to avoid repeated network requests. The `Cache` class (`network/cache.py`) uses file-based caching with SHA256 hashing of URLs.

**Features:**
- **TTL (Time To Live)**: Cache entries expire after 24 hours by default
- **Size Limits**: Cache automatically evicts oldest entries when size exceeds 100MB
- **Atomic Writes**: Cache writes use temporary files and atomic moves to prevent corruption
- **Memory Cache**: Frequently accessed entries are cached in memory for faster access

Cache management:
- `dpm cache info` - show cache size and location
- `dpm cache list` - list cached entries
- `dpm cache clear` - clear all cached data

## Virtual Environments

`VirtualEnv` (`installer/venv.py`) manages isolated environments:
- Creates Python venv via `python3 -m venv`
- Detects existing environments (conda, poetry, pipenv)
- Handles activation scripts

## Integrity Verification

`Installer` (`installer/installer.py`) handles package verification:
- Computes SHA256 hashes of downloaded packages
- Verifies against registry-provided integrity strings
- Uses the `sha256-<hex>` format
- Verifies packages are importable after installation (Python) or exist (npm)
- Automatically rolls back installations on verification failure

## Installation Plan

`InstallationPlan` (`installer/plan.py`) orders packages by dependencies:
- Uses topological sort to determine installation order
- Groups packages that can be installed in parallel
- Ensures dependencies are installed before dependents

## Configuration

`Config` (`core/config.py`) manages user and project settings:
- User config: `~/.dpm/config.json`
- Project config: `dpm.config.json` (optional)
- Supports: cache_dir, default_sources, timeout, max_workers, log_level

## Logging

`Logger` (`core/logger.py`) provides structured logging:
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Console and file logging
- Configurable log levels

## Export/Import

`Exporter` (`core/exporter.py`) handles format conversion:
- Export to `requirements.txt` (pip format)
- Export to `package.json` (npm format)
- Export lock file

## Repository Management

`RepositoryManager` (`core/repository.py`) manages custom repositories:
- Add/remove custom package sources
- Support for authenticated repositories
- Stored in `~/.dpm/repositories.json`

## Robustness Features

### Network Resilience

`HttpClient` (`network/http_client.py`) includes:
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts by default)
- **Timeout Protection**: 30-second timeout per request
- **Error Handling**: Handles HTTP errors, URL errors, and network failures gracefully
- **Rate Limit Handling**: Special handling for 429 (Too Many Requests) responses

### Input Validation

`Validation` (`core/validation.py`) provides:
- **Package Name Sanitization**: Prevents path traversal attacks and invalid characters
- **Version Validation**: Ensures version strings are valid semantic versions
- **Constraint Validation**: Validates version constraint syntax

### File Safety

- **Atomic Writes**: Lock files and cache use temporary files and atomic moves
- **Error Recovery**: Failed writes don't corrupt existing files
- **Transaction Safety**: All-or-nothing file operations

### Performance Optimizations

- **SystemSource Caching**: System package existence checks are cached to avoid expensive subprocess calls
- **Heuristic Filtering**: SystemSource skips checking packages that are clearly Python/JS packages
- **Subprocess Timeouts**: System package checks have 2-second timeouts to prevent hangs
- **Cache Size Optimization**: Cache size checks are performed periodically, not on every write

### Resolution Safety

- **Timeout Protection**: Resolution has a 60-second timeout to prevent infinite hangs
- **Error Reporting**: Detailed conflict information when resolution fails
- **Rollback Support**: Failed installations are automatically rolled back
