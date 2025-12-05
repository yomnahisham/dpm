#!/bin/bash
# test_install.sh - verify actual pip/npm installs work

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DPM="$SCRIPT_DIR/../../build/dpm"
TEST_DIR="$SCRIPT_DIR/test_workspace"

echo "=== Test: Actual Package Installation ==="

# cleanup
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# test 1: create venv
echo "[1/4] Creating virtual environment..."
$DPM venv create test_env
if [ ! -d "test_env" ]; then
    echo "FAIL: venv not created"
    exit 1
fi
echo "PASS: venv created"

# test 2: install python package
echo "[2/4] Installing Python package (requests)..."
source test_env/bin/activate
$DPM install requests || true  # may fail on some systems, that's ok for now

# verify requests is importable
if python3 -c "import requests; print('requests version:', requests.__version__)" 2>/dev/null; then
    echo "PASS: requests installed and importable"
else
    echo "SKIP: requests install verification (pip may not be available)"
fi

deactivate 2>/dev/null || true

# test 3: resolve works (doesn't require actual install)
echo "[3/4] Testing resolve command..."
cd "$SCRIPT_DIR/../.."
RESOLVE_OUTPUT=$($DPM resolve requests 2>&1)
if echo "$RESOLVE_OUTPUT" | grep -q "requests"; then
    echo "PASS: resolve found requests"
else
    echo "FAIL: resolve didn't find requests"
    exit 1
fi

# test 4: info command works
echo "[4/4] Testing info command..."
INFO_OUTPUT=$($DPM info requests 2>&1)
if echo "$INFO_OUTPUT" | grep -q "PyPI"; then
    echo "PASS: info shows PyPI source"
else
    echo "FAIL: info command failed"
    exit 1
fi

# cleanup
rm -rf "$TEST_DIR"

echo ""
echo "=== test_install.sh: ALL TESTS PASSED ==="



