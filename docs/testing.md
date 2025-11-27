# Testing DPM

Manual testing guide for DPM features.

## Setup

```bash
cd dpm/build
cmake ..
make -j4
```

## Basic Commands

### 1. Search for a package

```bash
./dpm search requests
./dpm search flask
./dpm search express    # npm package
```

### 2. Get package info

```bash
./dpm info requests
./dpm info numpy
./dpm info lodash       # npm package
```

### 3. Resolve dependencies (dry run)

```bash
# single package
./dpm resolve requests

# multiple packages
./dpm resolve flask django

# see the dependency tree
./dpm tree flask
./dpm tree requests
```

### 4. Create a lock file

```bash
./dpm lock requests flask
cat dpm.lock    # view the lock file
```

### 5. Install packages

```bash
# install specific packages
./dpm install requests

# install from lock file (after running lock command)
./dpm install
```

### 6. List installed packages

```bash
./dpm list
```

### 7. Remove packages

```bash
./dpm remove requests
```

### 8. Virtual environments

```bash
# create a venv
./dpm venv create

# check status
./dpm venv status

# activate manually
source .dpm_env/bin/activate

# deactivate
deactivate
```

## Test Scenarios

### Scenario 1: Simple Python package

```bash
./dpm resolve requests
# should show: requests, urllib3, idna, charset_normalizer, certifi
```

### Scenario 2: Package with many dependencies

```bash
./dpm tree flask
# should show flask and all its dependencies in tree format
```

### Scenario 3: Multiple packages

```bash
./dpm resolve numpy pandas matplotlib
# should resolve all three with their dependencies
```

### Scenario 4: npm package

```bash
./dpm info express
./dpm resolve lodash
```

### Scenario 5: Lock file workflow

```bash
# create lock file
./dpm lock requests flask

# verify lock file exists
cat dpm.lock

# install from lock file
./dpm install

# should use versions from lock file
```

### Scenario 6: Dependency tree

```bash
./dpm tree django
# should show django with all nested dependencies
```

## Expected Output Examples

### dpm info requests

```
+-- Package Info: requests ----------------------------+
-> Package details
  Name:     requests
  Version:  2.32.5 (latest)
  Language: python
  Source:   PyPI

-> Dependencies (4)
  * charset_normalizer
  * idna
  * urllib3
  * certifi

-> Available versions (157 total)
  * 2.32.5 (latest)
  * 2.32.4
  ...
+----------------------------------------------------+
```

### dpm tree flask

```
+-- Dependency Tree -----------------------------------+
flask 3.1.2
    |-- blinker 1.9.0
    |-- click 8.3.1
    |   `-- colorama 0.4.6
    |-- jinja2 3.1.2
    |   `-- markupsafe 3.0.3
    |-- werkzeug 3.1.2
    |   `-- markupsafe 3.0.3
    ...
+----------------------------------------------------+
```

## Troubleshooting

### "Package not found"

- check spelling
- verify the package exists on pypi.org or npmjs.com

### "Failed to resolve dependencies"

- might be a version conflict
- try `./dpm resolve <package>` to see what's happening

### Slow first run

- first run fetches from network
- subsequent runs use cache (~/.dpm/cache)

### Clear cache

```bash
rm -rf ~/.dpm/cache
```

## Performance Testing

```bash
# time a large resolution
time ./dpm resolve requests flask django numpy pandas scipy matplotlib

# should complete in a few seconds (cached) or ~10-20s (uncached)
```

