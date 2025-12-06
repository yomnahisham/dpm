# Testing DPM

Testing guide for DPM features.

## Setup

```bash
# clone the repository
git clone https://github.com/yomnahisham/dpm.git
cd dpm

# install in development mode
pip install -e .

# verify installation
dpm --version
```

## Unit Tests

Run unit tests:

```bash
# test version parsing and comparison
python3 tests/unit/test_version.py

# test dependency parsing
python3 tests/unit/test_dependency.py

# test graph operations
python3 tests/unit/test_graph.py

# run all tests
python3 tests/unit/test_version.py && \
python3 tests/unit/test_dependency.py && \
python3 tests/unit/test_graph.py
```

## Basic Commands

### 1. Search for a package

```bash
dpm search requests
dpm search flask
dpm search express    # npm package
```

### 2. Get package info

```bash
dpm info requests
dpm info numpy
dpm info lodash       # npm package
```

### 3. Resolve dependencies (dry run)

```bash
# single package
dpm resolve requests

# multiple packages
dpm resolve flask django

# see the dependency tree
dpm tree flask
dpm tree requests
```

### 4. Create a lock file

```bash
dpm lock requests flask
cat dpm.lock    # view the lock file
```

### 5. Install packages

```bash
# install specific packages
dpm install requests

# install from lock file (after running lock command)
dpm install
```

### 6. List installed packages

```bash
dpm list
```

### 7. Remove packages

```bash
dpm remove requests
```

### 8. Virtual environments

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

### 9. Manifest file

```bash
# initialize manifest
dpm init myproject 1.0.0

# view manifest
cat dpm.json
```

### 10. Package pinning

```bash
# pin a package
dpm pin requests@2.32.5

# unpin a package
dpm unpin requests
```

### 11. Export dependencies

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json
```

### 12. Cache management

```bash
# show cache info
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### 13. Check outdated packages

```bash
dpm outdated
```

### 14. Clean unused packages

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### 15. Repository management

```bash
# list repositories
dpm repo list

# add repository
dpm repo add myrepo https://example.com/repo

# remove repository
dpm repo remove myrepo
```

## Test Scenarios

### Scenario 1: Simple Python package

```bash
dpm resolve requests
# should show: requests, urllib3, idna, charset_normalizer, certifi
```

### Scenario 2: Package with many dependencies

```bash
dpm tree flask
# should show flask and all its dependencies in tree format
```

### Scenario 3: Multiple packages

```bash
dpm resolve numpy pandas matplotlib
# should resolve all three with their dependencies
```

### Scenario 4: npm package

```bash
dpm info express
dpm resolve lodash
```

### Scenario 5: Lock file workflow

```bash
# create lock file
dpm lock requests flask

# verify lock file exists
cat dpm.lock

# install from lock file
dpm install

# should use versions from lock file
```

### Scenario 6: Dependency tree

```bash
dpm tree django
# should show django with all nested dependencies
```

### Scenario 7: Manifest file workflow

```bash
# initialize project
dpm init myproject 1.0.0

# install packages (adds to manifest)
dpm install requests

# view manifest
cat dpm.json

# pin a package
dpm pin requests@2.32.5

# unpin
dpm unpin requests
```

### Scenario 8: Export/Import

```bash
# create lock file
dpm lock requests flask

# export to requirements.txt
dpm export requirements.txt
cat requirements.txt

# export to package.json
dpm export package.json
cat package.json
```

### Scenario 9: Offline mode

```bash
# first, resolve with network (populates cache)
dpm resolve requests

# then resolve offline
dpm --offline resolve requests
```

### Scenario 10: Verbose/Debug mode

```bash
# verbose output
dpm --verbose resolve requests

# debug output
dpm --debug resolve requests
```

### Scenario 11: Resolution details

```bash
# show detailed resolution steps
dpm --show-resolution resolve flask django
```

## Expected Output Examples

### dpm info requests

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

### dpm tree flask

```
Dependency tree:

`-- flask@3.1.2
    |-- blinker@1.9.0
    |-- click@8.3.1
    |   `-- colorama@0.4.6
    |-- jinja2@3.1.2
    |   `-- markupsafe@3.0.3
    |-- werkzeug@3.1.2
    |   `-- markupsafe@3.0.3
    ...
```

### dpm list

```
Installed packages (5):
  * certifi@2025.11.12
  * charset_normalizer@3.4.4
  * idna@3.11
  * requests@2.32.5
  * urllib3@1.26.20
```

## Troubleshooting

### "Package not found"

- Check spelling
- Verify the package exists on pypi.org or npmjs.com
- Try `dpm search <package>` to find similar packages

### "Failed to resolve dependencies"

- Might be a version conflict
- Try `dpm resolve <package>` to see what's happening
- Use `--show-resolution` for detailed information

### Slow first run

- First run fetches from network
- Subsequent runs use cache (`~/.dpm/cache`)
- Use `dpm cache info` to check cache status

### Clear cache

```bash
dpm cache clear
# or manually
rm -rf ~/.dpm/cache
```

### Integrity verification errors

- Package may have been corrupted
- Try clearing cache and re-downloading
- Use `--skip-integrity` to bypass (not recommended)

### Virtual environment issues

- Check if venv exists: `dpm venv status`
- Try detecting existing environments: `dpm venv detect`
- Create new venv: `dpm venv create myenv`

## Performance Testing

```bash
# time a large resolution
time dpm resolve requests flask django numpy pandas scipy matplotlib

# should complete in a few seconds (cached) or ~10-20s (uncached)
```

## Integration Testing

Test with real package installations:

```bash
# install packages
dpm install requests

# verify installation
dpm list

# check for updates
dpm outdated

# update packages
dpm update

# remove packages
dpm remove requests
```

## Test Coverage

Current test coverage:
- ✅ Version parsing and comparison
- ✅ Dependency constraint parsing
- ✅ Graph operations (add, dependencies, dependents)
- ✅ Cycle detection
- ✅ Topological sort
- ✅ Network retry logic
- ✅ Input validation
- ✅ Cache TTL and size limits
- ✅ Atomic file writes
- ✅ SystemSource optimization
- ✅ Resolution timeout
- ✅ Offline mode

## Robustness Testing

### Network Resilience

```bash
# test retry logic (simulate network failure)
# HttpClient automatically retries with exponential backoff
dpm resolve requests  # should retry on transient failures
```

### Input Validation

```bash
# test input sanitization
python3 -c "from dpm.core.validation import sanitize_package_name, ValidationError; \
  print('Valid:', sanitize_package_name('test-package')); \
  try: sanitize_package_name('../../etc/passwd'); \
  except ValidationError as e: print('Blocked:', type(e).__name__)"
```

### Cache TTL

```bash
# test cache expiration
python3 -c "from dpm.network.cache import Cache; import time; \
  cache = Cache(ttl_hours=0.001); cache.set('test', 'value'); \
  time.sleep(2); result = cache.get('test'); \
  print('TTL test:', 'Expired' if result is None else 'Still cached')"
```

### Atomic Writes

```bash
# test atomic file writes
python3 -c "from dpm.installer.lockfile import LockFile; \
  lf = LockFile('test.lock'); \
  result = lf.write({'test': '1.0.0'}, {}, {}); \
  print('Atomic write:', 'OK' if result else 'Failed')"
```

### Performance Testing

```bash
# test multiple packages resolution
time dpm resolve requests flask django numpy

# should complete in < 5 seconds (cached) or ~20-25s (uncached)
```

## Test Results Summary

See [Test Results](test_results.md) for comprehensive test results covering:
- Core functionality (6 tests)
- File management (4 tests)
- Management commands (5 tests)
- Advanced features (3 tests)
- Unit tests (3 suites)
- Performance tests (2 tests)
- Robustness tests (6 tests)

**Total: 28 tests, all passed ✅**

Testing guide for DPM features.

## Setup

```bash
# clone the repository
git clone https://github.com/yomnahisham/dpm.git
cd dpm

# install in development mode
pip install -e .

# verify installation
dpm --version
```

## Unit Tests

Run unit tests:

```bash
# test version parsing and comparison
python3 tests/unit/test_version.py

# test dependency parsing
python3 tests/unit/test_dependency.py

# test graph operations
python3 tests/unit/test_graph.py

# run all tests
python3 tests/unit/test_version.py && \
python3 tests/unit/test_dependency.py && \
python3 tests/unit/test_graph.py
```

## Basic Commands

### 1. Search for a package

```bash
dpm search requests
dpm search flask
dpm search express    # npm package
```

### 2. Get package info

```bash
dpm info requests
dpm info numpy
dpm info lodash       # npm package
```

### 3. Resolve dependencies (dry run)

```bash
# single package
dpm resolve requests

# multiple packages
dpm resolve flask django

# see the dependency tree
dpm tree flask
dpm tree requests
```

### 4. Create a lock file

```bash
dpm lock requests flask
cat dpm.lock    # view the lock file
```

### 5. Install packages

```bash
# install specific packages
dpm install requests

# install from lock file (after running lock command)
dpm install
```

### 6. List installed packages

```bash
dpm list
```

### 7. Remove packages

```bash
dpm remove requests
```

### 8. Virtual environments

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

### 9. Manifest file

```bash
# initialize manifest
dpm init myproject 1.0.0

# view manifest
cat dpm.json
```

### 10. Package pinning

```bash
# pin a package
dpm pin requests@2.32.5

# unpin a package
dpm unpin requests
```

### 11. Export dependencies

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json
```

### 12. Cache management

```bash
# show cache info
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### 13. Check outdated packages

```bash
dpm outdated
```

### 14. Clean unused packages

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### 15. Repository management

```bash
# list repositories
dpm repo list

# add repository
dpm repo add myrepo https://example.com/repo

# remove repository
dpm repo remove myrepo
```

## Test Scenarios

### Scenario 1: Simple Python package

```bash
dpm resolve requests
# should show: requests, urllib3, idna, charset_normalizer, certifi
```

### Scenario 2: Package with many dependencies

```bash
dpm tree flask
# should show flask and all its dependencies in tree format
```

### Scenario 3: Multiple packages

```bash
dpm resolve numpy pandas matplotlib
# should resolve all three with their dependencies
```

### Scenario 4: npm package

```bash
dpm info express
dpm resolve lodash
```

### Scenario 5: Lock file workflow

```bash
# create lock file
dpm lock requests flask

# verify lock file exists
cat dpm.lock

# install from lock file
dpm install

# should use versions from lock file
```

### Scenario 6: Dependency tree

```bash
dpm tree django
# should show django with all nested dependencies
```

### Scenario 7: Manifest file workflow

```bash
# initialize project
dpm init myproject 1.0.0

# install packages (adds to manifest)
dpm install requests

# view manifest
cat dpm.json

# pin a package
dpm pin requests@2.32.5

# unpin
dpm unpin requests
```

### Scenario 8: Export/Import

```bash
# create lock file
dpm lock requests flask

# export to requirements.txt
dpm export requirements.txt
cat requirements.txt

# export to package.json
dpm export package.json
cat package.json
```

### Scenario 9: Offline mode

```bash
# first, resolve with network (populates cache)
dpm resolve requests

# then resolve offline
dpm --offline resolve requests
```

### Scenario 10: Verbose/Debug mode

```bash
# verbose output
dpm --verbose resolve requests

# debug output
dpm --debug resolve requests
```

### Scenario 11: Resolution details

```bash
# show detailed resolution steps
dpm --show-resolution resolve flask django
```

## Expected Output Examples

### dpm info requests

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

### dpm tree flask

```
Dependency tree:

`-- flask@3.1.2
    |-- blinker@1.9.0
    |-- click@8.3.1
    |   `-- colorama@0.4.6
    |-- jinja2@3.1.2
    |   `-- markupsafe@3.0.3
    |-- werkzeug@3.1.2
    |   `-- markupsafe@3.0.3
    ...
```

### dpm list

```
Installed packages (5):
  * certifi@2025.11.12
  * charset_normalizer@3.4.4
  * idna@3.11
  * requests@2.32.5
  * urllib3@1.26.20
```

## Troubleshooting

### "Package not found"

- Check spelling
- Verify the package exists on pypi.org or npmjs.com
- Try `dpm search <package>` to find similar packages

### "Failed to resolve dependencies"

- Might be a version conflict
- Try `dpm resolve <package>` to see what's happening
- Use `--show-resolution` for detailed information

### Slow first run

- First run fetches from network
- Subsequent runs use cache (`~/.dpm/cache`)
- Use `dpm cache info` to check cache status

### Clear cache

```bash
dpm cache clear
# or manually
rm -rf ~/.dpm/cache
```

### Integrity verification errors

- Package may have been corrupted
- Try clearing cache and re-downloading
- Use `--skip-integrity` to bypass (not recommended)

### Virtual environment issues

- Check if venv exists: `dpm venv status`
- Try detecting existing environments: `dpm venv detect`
- Create new venv: `dpm venv create myenv`

## Performance Testing

```bash
# time a large resolution
time dpm resolve requests flask django numpy pandas scipy matplotlib

# should complete in a few seconds (cached) or ~10-20s (uncached)
```

## Integration Testing

Test with real package installations:

```bash
# install packages
dpm install requests

# verify installation
dpm list

# check for updates
dpm outdated

# update packages
dpm update

# remove packages
dpm remove requests
```

## Test Coverage

Current test coverage:
- ✅ Version parsing and comparison
- ✅ Dependency constraint parsing
- ✅ Graph operations (add, dependencies, dependents)
- ✅ Cycle detection
- ✅ Topological sort
- ✅ Network retry logic
- ✅ Input validation
- ✅ Cache TTL and size limits
- ✅ Atomic file writes
- ✅ SystemSource optimization
- ✅ Resolution timeout
- ✅ Offline mode

## Robustness Testing

### Network Resilience

```bash
# test retry logic (simulate network failure)
# HttpClient automatically retries with exponential backoff
dpm resolve requests  # should retry on transient failures
```

### Input Validation

```bash
# test input sanitization
python3 -c "from dpm.core.validation import sanitize_package_name, ValidationError; \
  print('Valid:', sanitize_package_name('test-package')); \
  try: sanitize_package_name('../../etc/passwd'); \
  except ValidationError as e: print('Blocked:', type(e).__name__)"
```

### Cache TTL

```bash
# test cache expiration
python3 -c "from dpm.network.cache import Cache; import time; \
  cache = Cache(ttl_hours=0.001); cache.set('test', 'value'); \
  time.sleep(2); result = cache.get('test'); \
  print('TTL test:', 'Expired' if result is None else 'Still cached')"
```

### Atomic Writes

```bash
# test atomic file writes
python3 -c "from dpm.installer.lockfile import LockFile; \
  lf = LockFile('test.lock'); \
  result = lf.write({'test': '1.0.0'}, {}, {}); \
  print('Atomic write:', 'OK' if result else 'Failed')"
```

### Performance Testing

```bash
# test multiple packages resolution
time dpm resolve requests flask django numpy

# should complete in < 5 seconds (cached) or ~20-25s (uncached)
```

## Test Results Summary

See [Test Results](test_results.md) for comprehensive test results covering:
- Core functionality (6 tests)
- File management (4 tests)
- Management commands (5 tests)
- Advanced features (3 tests)
- Unit tests (3 suites)
- Performance tests (2 tests)
- Robustness tests (6 tests)

**Total: 28 tests, all passed ✅**

Testing guide for DPM features.

## Setup

```bash
# clone the repository
git clone https://github.com/yomnahisham/dpm.git
cd dpm

# install in development mode
pip install -e .

# verify installation
dpm --version
```

## Unit Tests

Run unit tests:

```bash
# test version parsing and comparison
python3 tests/unit/test_version.py

# test dependency parsing
python3 tests/unit/test_dependency.py

# test graph operations
python3 tests/unit/test_graph.py

# run all tests
python3 tests/unit/test_version.py && \
python3 tests/unit/test_dependency.py && \
python3 tests/unit/test_graph.py
```

## Basic Commands

### 1. Search for a package

```bash
dpm search requests
dpm search flask
dpm search express    # npm package
```

### 2. Get package info

```bash
dpm info requests
dpm info numpy
dpm info lodash       # npm package
```

### 3. Resolve dependencies (dry run)

```bash
# single package
dpm resolve requests

# multiple packages
dpm resolve flask django

# see the dependency tree
dpm tree flask
dpm tree requests
```

### 4. Create a lock file

```bash
dpm lock requests flask
cat dpm.lock    # view the lock file
```

### 5. Install packages

```bash
# install specific packages
dpm install requests

# install from lock file (after running lock command)
dpm install
```

### 6. List installed packages

```bash
dpm list
```

### 7. Remove packages

```bash
dpm remove requests
```

### 8. Virtual environments

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

### 9. Manifest file

```bash
# initialize manifest
dpm init myproject 1.0.0

# view manifest
cat dpm.json
```

### 10. Package pinning

```bash
# pin a package
dpm pin requests@2.32.5

# unpin a package
dpm unpin requests
```

### 11. Export dependencies

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json
```

### 12. Cache management

```bash
# show cache info
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### 13. Check outdated packages

```bash
dpm outdated
```

### 14. Clean unused packages

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### 15. Repository management

```bash
# list repositories
dpm repo list

# add repository
dpm repo add myrepo https://example.com/repo

# remove repository
dpm repo remove myrepo
```

## Test Scenarios

### Scenario 1: Simple Python package

```bash
dpm resolve requests
# should show: requests, urllib3, idna, charset_normalizer, certifi
```

### Scenario 2: Package with many dependencies

```bash
dpm tree flask
# should show flask and all its dependencies in tree format
```

### Scenario 3: Multiple packages

```bash
dpm resolve numpy pandas matplotlib
# should resolve all three with their dependencies
```

### Scenario 4: npm package

```bash
dpm info express
dpm resolve lodash
```

### Scenario 5: Lock file workflow

```bash
# create lock file
dpm lock requests flask

# verify lock file exists
cat dpm.lock

# install from lock file
dpm install

# should use versions from lock file
```

### Scenario 6: Dependency tree

```bash
dpm tree django
# should show django with all nested dependencies
```

### Scenario 7: Manifest file workflow

```bash
# initialize project
dpm init myproject 1.0.0

# install packages (adds to manifest)
dpm install requests

# view manifest
cat dpm.json

# pin a package
dpm pin requests@2.32.5

# unpin
dpm unpin requests
```

### Scenario 8: Export/Import

```bash
# create lock file
dpm lock requests flask

# export to requirements.txt
dpm export requirements.txt
cat requirements.txt

# export to package.json
dpm export package.json
cat package.json
```

### Scenario 9: Offline mode

```bash
# first, resolve with network (populates cache)
dpm resolve requests

# then resolve offline
dpm --offline resolve requests
```

### Scenario 10: Verbose/Debug mode

```bash
# verbose output
dpm --verbose resolve requests

# debug output
dpm --debug resolve requests
```

### Scenario 11: Resolution details

```bash
# show detailed resolution steps
dpm --show-resolution resolve flask django
```

## Expected Output Examples

### dpm info requests

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

### dpm tree flask

```
Dependency tree:

`-- flask@3.1.2
    |-- blinker@1.9.0
    |-- click@8.3.1
    |   `-- colorama@0.4.6
    |-- jinja2@3.1.2
    |   `-- markupsafe@3.0.3
    |-- werkzeug@3.1.2
    |   `-- markupsafe@3.0.3
    ...
```

### dpm list

```
Installed packages (5):
  * certifi@2025.11.12
  * charset_normalizer@3.4.4
  * idna@3.11
  * requests@2.32.5
  * urllib3@1.26.20
```

## Troubleshooting

### "Package not found"

- Check spelling
- Verify the package exists on pypi.org or npmjs.com
- Try `dpm search <package>` to find similar packages

### "Failed to resolve dependencies"

- Might be a version conflict
- Try `dpm resolve <package>` to see what's happening
- Use `--show-resolution` for detailed information

### Slow first run

- First run fetches from network
- Subsequent runs use cache (`~/.dpm/cache`)
- Use `dpm cache info` to check cache status

### Clear cache

```bash
dpm cache clear
# or manually
rm -rf ~/.dpm/cache
```

### Integrity verification errors

- Package may have been corrupted
- Try clearing cache and re-downloading
- Use `--skip-integrity` to bypass (not recommended)

### Virtual environment issues

- Check if venv exists: `dpm venv status`
- Try detecting existing environments: `dpm venv detect`
- Create new venv: `dpm venv create myenv`

## Performance Testing

```bash
# time a large resolution
time dpm resolve requests flask django numpy pandas scipy matplotlib

# should complete in a few seconds (cached) or ~10-20s (uncached)
```

## Integration Testing

Test with real package installations:

```bash
# install packages
dpm install requests

# verify installation
dpm list

# check for updates
dpm outdated

# update packages
dpm update

# remove packages
dpm remove requests
```

## Test Coverage

Current test coverage:
- ✅ Version parsing and comparison
- ✅ Dependency constraint parsing
- ✅ Graph operations (add, dependencies, dependents)
- ✅ Cycle detection
- ✅ Topological sort
- ✅ Network retry logic
- ✅ Input validation
- ✅ Cache TTL and size limits
- ✅ Atomic file writes
- ✅ SystemSource optimization
- ✅ Resolution timeout
- ✅ Offline mode

## Robustness Testing

### Network Resilience

```bash
# test retry logic (simulate network failure)
# HttpClient automatically retries with exponential backoff
dpm resolve requests  # should retry on transient failures
```

### Input Validation

```bash
# test input sanitization
python3 -c "from dpm.core.validation import sanitize_package_name, ValidationError; \
  print('Valid:', sanitize_package_name('test-package')); \
  try: sanitize_package_name('../../etc/passwd'); \
  except ValidationError as e: print('Blocked:', type(e).__name__)"
```

### Cache TTL

```bash
# test cache expiration
python3 -c "from dpm.network.cache import Cache; import time; \
  cache = Cache(ttl_hours=0.001); cache.set('test', 'value'); \
  time.sleep(2); result = cache.get('test'); \
  print('TTL test:', 'Expired' if result is None else 'Still cached')"
```

### Atomic Writes

```bash
# test atomic file writes
python3 -c "from dpm.installer.lockfile import LockFile; \
  lf = LockFile('test.lock'); \
  result = lf.write({'test': '1.0.0'}, {}, {}); \
  print('Atomic write:', 'OK' if result else 'Failed')"
```

### Performance Testing

```bash
# test multiple packages resolution
time dpm resolve requests flask django numpy

# should complete in < 5 seconds (cached) or ~20-25s (uncached)
```

## Test Results Summary

See [Test Results](test_results.md) for comprehensive test results covering:
- Core functionality (6 tests)
- File management (4 tests)
- Management commands (5 tests)
- Advanced features (3 tests)
- Unit tests (3 suites)
- Performance tests (2 tests)
- Robustness tests (6 tests)

**Total: 28 tests, all passed ✅**

Testing guide for DPM features.

## Setup

```bash
# clone the repository
git clone https://github.com/yomnahisham/dpm.git
cd dpm

# install in development mode
pip install -e .

# verify installation
dpm --version
```

## Unit Tests

Run unit tests:

```bash
# test version parsing and comparison
python3 tests/unit/test_version.py

# test dependency parsing
python3 tests/unit/test_dependency.py

# test graph operations
python3 tests/unit/test_graph.py

# run all tests
python3 tests/unit/test_version.py && \
python3 tests/unit/test_dependency.py && \
python3 tests/unit/test_graph.py
```

## Basic Commands

### 1. Search for a package

```bash
dpm search requests
dpm search flask
dpm search express    # npm package
```

### 2. Get package info

```bash
dpm info requests
dpm info numpy
dpm info lodash       # npm package
```

### 3. Resolve dependencies (dry run)

```bash
# single package
dpm resolve requests

# multiple packages
dpm resolve flask django

# see the dependency tree
dpm tree flask
dpm tree requests
```

### 4. Create a lock file

```bash
dpm lock requests flask
cat dpm.lock    # view the lock file
```

### 5. Install packages

```bash
# install specific packages
dpm install requests

# install from lock file (after running lock command)
dpm install
```

### 6. List installed packages

```bash
dpm list
```

### 7. Remove packages

```bash
dpm remove requests
```

### 8. Virtual environments

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

### 9. Manifest file

```bash
# initialize manifest
dpm init myproject 1.0.0

# view manifest
cat dpm.json
```

### 10. Package pinning

```bash
# pin a package
dpm pin requests@2.32.5

# unpin a package
dpm unpin requests
```

### 11. Export dependencies

```bash
# export to requirements.txt
dpm export requirements.txt

# export to package.json
dpm export package.json
```

### 12. Cache management

```bash
# show cache info
dpm cache info

# list cached entries
dpm cache list

# clear cache
dpm cache clear
```

### 13. Check outdated packages

```bash
dpm outdated
```

### 14. Clean unused packages

```bash
# preview what would be removed
dpm clean --dry-run

# actually remove
dpm clean
```

### 15. Repository management

```bash
# list repositories
dpm repo list

# add repository
dpm repo add myrepo https://example.com/repo

# remove repository
dpm repo remove myrepo
```

## Test Scenarios

### Scenario 1: Simple Python package

```bash
dpm resolve requests
# should show: requests, urllib3, idna, charset_normalizer, certifi
```

### Scenario 2: Package with many dependencies

```bash
dpm tree flask
# should show flask and all its dependencies in tree format
```

### Scenario 3: Multiple packages

```bash
dpm resolve numpy pandas matplotlib
# should resolve all three with their dependencies
```

### Scenario 4: npm package

```bash
dpm info express
dpm resolve lodash
```

### Scenario 5: Lock file workflow

```bash
# create lock file
dpm lock requests flask

# verify lock file exists
cat dpm.lock

# install from lock file
dpm install

# should use versions from lock file
```

### Scenario 6: Dependency tree

```bash
dpm tree django
# should show django with all nested dependencies
```

### Scenario 7: Manifest file workflow

```bash
# initialize project
dpm init myproject 1.0.0

# install packages (adds to manifest)
dpm install requests

# view manifest
cat dpm.json

# pin a package
dpm pin requests@2.32.5

# unpin
dpm unpin requests
```

### Scenario 8: Export/Import

```bash
# create lock file
dpm lock requests flask

# export to requirements.txt
dpm export requirements.txt
cat requirements.txt

# export to package.json
dpm export package.json
cat package.json
```

### Scenario 9: Offline mode

```bash
# first, resolve with network (populates cache)
dpm resolve requests

# then resolve offline
dpm --offline resolve requests
```

### Scenario 10: Verbose/Debug mode

```bash
# verbose output
dpm --verbose resolve requests

# debug output
dpm --debug resolve requests
```

### Scenario 11: Resolution details

```bash
# show detailed resolution steps
dpm --show-resolution resolve flask django
```

## Expected Output Examples

### dpm info requests

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

### dpm tree flask

```
Dependency tree:

`-- flask@3.1.2
    |-- blinker@1.9.0
    |-- click@8.3.1
    |   `-- colorama@0.4.6
    |-- jinja2@3.1.2
    |   `-- markupsafe@3.0.3
    |-- werkzeug@3.1.2
    |   `-- markupsafe@3.0.3
    ...
```

### dpm list

```
Installed packages (5):
  * certifi@2025.11.12
  * charset_normalizer@3.4.4
  * idna@3.11
  * requests@2.32.5
  * urllib3@1.26.20
```

## Troubleshooting

### "Package not found"

- Check spelling
- Verify the package exists on pypi.org or npmjs.com
- Try `dpm search <package>` to find similar packages

### "Failed to resolve dependencies"

- Might be a version conflict
- Try `dpm resolve <package>` to see what's happening
- Use `--show-resolution` for detailed information

### Slow first run

- First run fetches from network
- Subsequent runs use cache (`~/.dpm/cache`)
- Use `dpm cache info` to check cache status

### Clear cache

```bash
dpm cache clear
# or manually
rm -rf ~/.dpm/cache
```

### Integrity verification errors

- Package may have been corrupted
- Try clearing cache and re-downloading
- Use `--skip-integrity` to bypass (not recommended)

### Virtual environment issues

- Check if venv exists: `dpm venv status`
- Try detecting existing environments: `dpm venv detect`
- Create new venv: `dpm venv create myenv`

## Performance Testing

```bash
# time a large resolution
time dpm resolve requests flask django numpy pandas scipy matplotlib

# should complete in a few seconds (cached) or ~10-20s (uncached)
```

## Integration Testing

Test with real package installations:

```bash
# install packages
dpm install requests

# verify installation
dpm list

# check for updates
dpm outdated

# update packages
dpm update

# remove packages
dpm remove requests
```

## Test Coverage

Current test coverage:
- ✅ Version parsing and comparison
- ✅ Dependency constraint parsing
- ✅ Graph operations (add, dependencies, dependents)
- ✅ Cycle detection
- ✅ Topological sort
- ✅ Network retry logic
- ✅ Input validation
- ✅ Cache TTL and size limits
- ✅ Atomic file writes
- ✅ SystemSource optimization
- ✅ Resolution timeout
- ✅ Offline mode

## Robustness Testing

### Network Resilience

```bash
# test retry logic (simulate network failure)
# HttpClient automatically retries with exponential backoff
dpm resolve requests  # should retry on transient failures
```

### Input Validation

```bash
# test input sanitization
python3 -c "from dpm.core.validation import sanitize_package_name, ValidationError; \
  print('Valid:', sanitize_package_name('test-package')); \
  try: sanitize_package_name('../../etc/passwd'); \
  except ValidationError as e: print('Blocked:', type(e).__name__)"
```

### Cache TTL

```bash
# test cache expiration
python3 -c "from dpm.network.cache import Cache; import time; \
  cache = Cache(ttl_hours=0.001); cache.set('test', 'value'); \
  time.sleep(2); result = cache.get('test'); \
  print('TTL test:', 'Expired' if result is None else 'Still cached')"
```

### Atomic Writes

```bash
# test atomic file writes
python3 -c "from dpm.installer.lockfile import LockFile; \
  lf = LockFile('test.lock'); \
  result = lf.write({'test': '1.0.0'}, {}, {}); \
  print('Atomic write:', 'OK' if result else 'Failed')"
```

### Performance Testing

```bash
# test multiple packages resolution
time dpm resolve requests flask django numpy

# should complete in < 5 seconds (cached) or ~20-25s (uncached)
```

## Test Results Summary

See [Test Results](test_results.md) for comprehensive test results covering:
- Core functionality (6 tests)
- File management (4 tests)
- Management commands (5 tests)
- Advanced features (3 tests)
- Unit tests (3 suites)
- Performance tests (2 tests)
- Robustness tests (6 tests)

**Total: 28 tests, all passed ✅**
