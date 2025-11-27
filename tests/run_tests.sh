#!/bin/bash

set -e

echo "Building DPM..."
cd "$(dirname "$0")/.."
mkdir -p build
cd build
cmake .. > /dev/null
make -j4 2>&1 | grep -E "(error|warning:|Building)" || true

echo ""
echo "Building tests..."

# Compile tests
g++ -std=c++20 -I../src -o test_version ../tests/test_version.cpp ../src/core/version.cpp
g++ -std=c++20 -I../src -o test_dependency ../tests/test_dependency.cpp ../src/core/dependency.cpp ../src/core/version.cpp
g++ -std=c++20 -I../src -o test_graph ../tests/test_graph.cpp ../src/resolver/graph.cpp ../src/core/package.cpp ../src/core/version.cpp ../src/core/dependency.cpp

# Run tests
echo ""
echo "Running tests..."
echo ""

./test_version
./test_dependency
./test_graph

echo ""
echo "================================"
echo "All tests completed successfully!"
echo "================================"
