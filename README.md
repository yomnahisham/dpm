# DPM - Dependency Package Manager
```
  ____  ____  __  __ 
 |  _ \|  _ \|  \/  |
 | | | | |_) | |\/| |
 | |_| |  __/| |  | |
 |____/|_|   |_|  |_|
```

A cross-language package manager written in C++ that resolves dependencies using a hybrid greedy/backtracking algorithm.


## What it does

DPM fetches packages from PyPI, npm, and system package managers, figures out which versions work together, and installs them. It handles the annoying "dependency hell" problem where package A needs version X of something but package B needs version Y.

## Quick Start

```bash
# build it
git clone https://github.com/yomnahisham/dpm.git
cd dpm && mkdir build && cd build
cmake .. && make

# try it out
./dpm install requests flask
./dpm tree requests
./dpm info numpy
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `install` | install packages | `dpm install numpy pandas` |
| `remove` | uninstall packages | `dpm remove flask` |
| `update` | update to latest versions | `dpm update requests` |
| `list` | show installed packages | `dpm list` |
| `resolve` | dry run - show what would install | `dpm resolve django` |
| `tree` | show dependency tree | `dpm tree flask` |
| `info` | show package details | `dpm info requests` |
| `search` | find packages | `dpm search flask` |
| `lock` | generate lock file | `dpm lock requests flask` |
| `venv` | manage virtual environment | `dpm venv create` |

### Lock Files

DPM creates a `dpm.lock` file to ensure reproducible installs:

```bash
dpm lock requests flask    # creates dpm.lock
dpm install                # installs from lock file
```

## How the Algorithm Works

DPM uses a **hybrid approach** - try the fast way first, fall back to the thorough way if needed.

### 1. Greedy (fast path)

```
for each package:
    pick the latest version that satisfies all constraints
    if conflict -> give up and try backtracking
```

Works for ~90% of cases. O(V+E) time complexity where V = packages, E = dependencies.

### 2. Backtracking (when greedy fails)

```
pick unassigned package with fewest valid versions (MRV heuristic)
for each possible version:
    if forward_check passes:  # would this break anything?
        assign version
        if backtrack(remaining) succeeds:
            return success
        unassign version
return failure
```

Uses constraint propagation and memoization to avoid redundant work. Worst case O(b^d) but usually much faster.

### Why hybrid?

- Greedy alone: fast but incomplete (can't handle some conflicts)
- Backtracking alone: complete but slow
- Hybrid: fast when possible, complete when necessary

## Package Sources

| Source | Language | API |
|--------|----------|-----|
| PyPI | Python | `pypi.org/pypi/{pkg}/json` |
| npm | JavaScript | `registry.npmjs.org/{pkg}` |
| System | varies | apt/yum commands |
| Local | any | JSON files |

## Building

**Requirements:**
- C++20 compiler (GCC 10+, Clang 12+)
- CMake 3.15+
- libcurl

**Ubuntu/Debian:**
```bash
sudo apt install build-essential cmake libcurl4-openssl-dev
```

**macOS:**
```bash
brew install cmake curl
```

**Build:**
```bash
mkdir build && cd build
cmake ..
make -j4
```

## Project Structure

```
src/
├── core/           # basic data types
│   ├── package     # package metadata
│   ├── version     # semver parsing and comparison
│   └── dependency  # version constraints
├── resolver/       # the algorithm stuff
│   ├── resolver    # main entry point, hybrid logic
│   ├── greedy      # fast greedy solver
│   ├── backtrack   # csp-style backtracking
│   └── graph       # dependency graph, cycle detection
├── sources/        # where we get packages from
│   ├── pypi        # python packages
│   ├── npm         # javascript packages
│   ├── system      # apt/yum
│   └── local       # json files for testing
├── installer/      # actually installs stuff
│   ├── installer   # calls pip/npm/apt
│   ├── plan        # installation ordering
│   ├── state       # tracks what's installed
│   └── lockfile    # dpm.lock handling
├── network/        # http and caching
│   ├── http_client # libcurl wrapper
│   └── cache       # disk cache for api responses
└── cli/            # command line interface
    └── commands    # install, remove, list, etc
```

## Example Output

```
$ ./dpm tree flask

+-- Dependency Tree -----------------------------------+

flask 3.1.2
    |-- blinker 1.9.0
    |-- click 8.3.1
    |   `-- colorama 0.4.6
    |-- importlib-metadata 8.7.0
    |   |-- zipp 3.23.0
    |   `-- typing-extensions 4.15.0
    |-- itsdangerous 2.2.0
    |-- jinja2 3.1.2
    |   `-- markupsafe 3.0.3
    `-- werkzeug 3.1.2
        `-- markupsafe 3.0.3

Total: 12 packages
+----------------------------------------------------+
```

## Features

- [x] greedy dependency resolution
- [x] backtracking with constraint propagation
- [x] pypi and npm support
- [x] parallel fetching for speed
- [x] response caching
- [x] lock file support
- [x] dependency tree visualization
- [x] progress bars and colored output
- [x] integrity verification (sha256 checksums)
- [x] virtual environments

## License

MIT
