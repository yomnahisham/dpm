# Installation Guide

## Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection (for initial setup and package fetching)

## Installation Methods

### Method 1: Development Installation (Recommended)

For development or testing:

```bash
# clone the repository
git clone https://github.com/yomnahisham/dpm.git
cd dpm

# install in development mode
pip install -e .

# verify installation
dpm --version
```

### Method 2: Global Installation

For system-wide installation:

```bash
# clone the repository
git clone https://github.com/yomnahisham/dpm.git
cd dpm

# install globally
pip install .

# verify installation
dpm --version
```

### Method 3: Direct Execution

Run without installation:

```bash
# clone the repository
git clone https://github.com/yomnahisham/dpm.git
cd dpm

# run directly
python3 -m dpm.main --version
python3 -m dpm.main install requests
```

## Post-Installation

### Verify Installation

```bash
# check version
dpm --version

# check help
dpm --help

# test basic command
dpm search requests
```

### Initial Setup

DPM will create configuration directories on first use:

- `~/.dpm/cache/` - Package metadata cache
- `~/.dpm/config.json` - User configuration
- `~/.dpm/repositories.json` - Custom repositories
- `~/.dpm/dpm.log` - Log file (if logging enabled)

## Troubleshooting

### "command not found: dpm"

If `dpm` command is not found:

1. Check if pip installed to a location in your PATH:
   ```bash
   python3 -m pip show dpm
   ```

2. Add pip's bin directory to PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. Or use direct execution:
   ```bash
   python3 -m dpm.main --help
   ```

### Permission Errors

If you get permission errors:

1. Use `--user` flag:
   ```bash
   pip install --user -e .
   ```

2. Or use a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

### Import Errors

If you get import errors:

1. Make sure you're in the project directory
2. Check Python version: `python3 --version` (should be 3.8+)
3. Reinstall: `pip install --force-reinstall -e .`

## Uninstallation

To uninstall DPM:

```bash
pip uninstall dpm
```

To remove configuration and cache:

```bash
rm -rf ~/.dpm
```

## Platform-Specific Notes

### macOS

No special requirements. Works out of the box.

### Linux

May need to install Python development headers:

```bash
# Ubuntu/Debian
sudo apt install python3-dev

# Fedora/RHEL
sudo dnf install python3-devel
```

### Windows

Works with Python 3.8+ installed from python.org. Use PowerShell or Command Prompt.

## Robustness Features

DPM includes built-in robustness features that work automatically:

- **Network resilience**: Automatic retries on network failures
- **Input validation**: Security protection against malicious inputs
- **Cache management**: Automatic TTL and size management
- **Installation safety**: Automatic rollback on failures
- **Timeout protection**: Prevents infinite hangs

These features are enabled by default. See [Robustness Guide](../docs/ROBUSTNESS.md) for configuration options.

## Next Steps

After installation:

1. Initialize a project: `dpm init myproject 1.0.0`
2. Install packages: `dpm install requests`
3. Explore commands: `dpm --help`

See [CLI Reference](cli.md) for detailed command usage.

