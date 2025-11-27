# Architecture

DPM is organized into several modules:

```
src/
├── core/           # Data structures (Package, Version, Dependency)
├── resolver/       # Dependency resolution algorithms
├── sources/        # Package registry integrations
├── installer/      # Installation, venv, integrity checking
├── network/        # HTTP client and caching
└── cli/            # Command handlers
```

## Resolution Flow

1. User requests packages via CLI
2. `CommandHandler` parses input and initializes sources
3. `DependencyResolver` attempts resolution:
   - Tries `GreedyResolver` first (fast path)
   - Falls back to `BacktrackResolver` if conflicts found
4. Resolution result contains selected versions for all packages
5. `Installer` executes the plan in dependency order

## Key Components

### DependencyResolver

The hybrid resolver (`resolver/resolver.hpp`) coordinates between greedy and backtracking approaches. It returns a `ResolutionResult`:

```cpp
struct ResolutionResult {
    bool success;
    map<string, string> selected_versions;  // package -> version
    string error_message;
    bool used_backtracking;
};
```

### Version Constraints

Supported constraint operators (`core/version.hpp`):
- `==`, `!=`, `<`, `<=`, `>`, `>=`
- `~` (tilde): allows patch updates (`~1.2.3` = `>=1.2.3,<1.3.0`)
- `^` (caret): allows minor updates (`^1.2.3` = `>=1.2.3,<2.0.0`)

Multiple constraints can be combined: `>=1.0.0,<2.0.0`

### Sources

Each source implements the `Source` interface:
- `getAvailableVersions(package_name)` - returns all versions
- `getDependencies(package_name, version)` - returns dependencies for a specific version
- `getPackageInfo(package_name)` - metadata lookup

Current implementations: PyPI, npm, system (apt/yum), local JSON files.

## Caching

HTTP responses are cached in `~/.dpm/cache/` to avoid repeated network requests. Cache entries expire after a configurable TTL.

## Virtual Environments

`VirtualEnv` (`installer/venv.hpp`) manages isolated environments:
- Creates Python venv via `python3 -m venv`
- Sets up local `node_modules` for npm packages
- Handles PATH manipulation for activation/deactivation

## Integrity

`IntegrityChecker` (`installer/integrity.hpp`) handles package verification:
- Computes SHA256 hashes of downloaded packages
- Verifies against registry-provided integrity strings
- Uses the `sha256-<base64>` format (same as npm)

