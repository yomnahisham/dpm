# Quick Start Guide

Get started with DPM in 5 minutes.

## Installation

```bash
git clone https://github.com/yomnahisham/dpm.git
cd dpm
pip install -e .
```

## Basic Workflow

### 1. Initialize a Project

```bash
dpm init myproject 1.0.0
```

This creates a `dpm.json` file.

### 2. Install Packages

```bash
# install Python packages
dpm install requests numpy

# install npm packages
dpm install express lodash
```

### 3. View Dependencies

```bash
# see what's installed
dpm list

# see dependency tree
dpm tree requests

# see package info
dpm info requests
```

### 4. Create Lock File

```bash
dpm lock requests numpy
```

This creates `dpm.lock` with exact versions.

### 5. Install from Lock File

```bash
dpm install
```

Installs exact versions from `dpm.lock` for reproducibility.

## Common Commands

```bash
# search for packages
dpm search flask

# update packages
dpm update

# check for outdated packages
dpm outdated

# remove packages
dpm remove flask

# export to requirements.txt
dpm export requirements.txt
```

## Virtual Environments

```bash
# create venv
dpm venv create myenv

# check status
dpm venv status
```

## Advanced Features

### Package Pinning

```bash
# pin to exact version
dpm pin requests@2.32.5

# unpin (allow updates)
dpm unpin requests
```

### Offline Mode

```bash
# use cache only
dpm --offline resolve requests
```

### Verbose Output

```bash
# show detailed output
dpm --verbose resolve requests

# show debug info
dpm --debug resolve requests
```

## Robustness Features

DPM includes automatic robustness features:

- **Network resilience**: Automatic retry with exponential backoff
- **Input validation**: Prevents security issues
- **Cache management**: TTL and size limits
- **Installation safety**: Automatic rollback on failure
- **Timeout protection**: Prevents hangs

See [Robustness Guide](ROBUSTNESS.md) for details.

## Next Steps

- Read [CLI Reference](cli.md) for all commands
- See [Architecture](architecture.md) for how it works
- Check [Testing Guide](testing.md) for examples
- Learn about [Robustness Features](ROBUSTNESS.md)

