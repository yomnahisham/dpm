# CLI Reference

## Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `install <packages...>` | `i` | Install packages and their dependencies |
| `update <packages...>` | `u` | Update packages to latest compatible versions |
| `remove <packages...>` | `rm`, `uninstall` | Remove installed packages |
| `list` | `ls` | List all installed packages |
| `resolve <packages...>` | `r` | Show resolution plan without installing (dry run) |
| `tree <packages...>` | `t` | Display dependency tree |
| `lock <packages...>` | - | Generate lock file without installing |
| `search <query>` | `s` | Search for packages |
| `info <package>` | - | Show package details |
| `venv create [name]` | - | Create virtual environment (default: `.dpm_env`) |
| `venv activate` | - | Activate the virtual environment |
| `venv deactivate` | - | Deactivate the virtual environment |
| `venv status` | - | Show virtual environment status |

## Flags

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show usage information |
| `--version`, `-v` | Show version |

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
```

## Lock Files

Running `dpm lock` or `dpm install` generates a `dpm.lock` file in the current directory. This file pins exact versions for reproducible installs.

## Virtual Environments

DPM can create isolated environments to avoid polluting global installs:

```bash
# create a venv (defaults to .dpm_env)
dpm venv create

# or with a custom name
dpm venv create myenv

# activate it
dpm venv activate

# check status
dpm venv status

# deactivate when done
dpm venv deactivate
```

The venv includes both Python (via `python -m venv`) and a local `node_modules` directory. When activated, `dpm install` will install packages into the isolated environment.

## Integrity Verification

DPM verifies package integrity using SHA256 checksums. When packages are downloaded, their hashes are checked against the registry-provided integrity strings (in the format `sha256-<base64>`). This prevents tampered or corrupted packages from being installed.

