cmake_minimum_required(VERSION 3.15)
project(DPM VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")

# Find required packages
find_package(CURL REQUIRED)

# Suppress warnings for third-party headers
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-unused-parameter")

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/src)

# Source files
set(SOURCES
    src/main.cpp
    src/core/package.cpp
    src/core/version.cpp
    src/core/dependency.cpp
    src/resolver/resolver.cpp
    src/resolver/greedy.cpp
    src/resolver/backtrack.cpp
    src/resolver/graph.cpp
    src/sources/source.cpp
    src/sources/pypi.cpp
    src/sources/npm.cpp
    src/sources/system.cpp
    src/sources/local.cpp
    src/installer/installer.cpp
    src/installer/plan.cpp
    src/installer/lockfile.cpp
    src/installer/venv.cpp
    src/installer/integrity.cpp
    src/network/http_client.cpp
    src/network/cache.cpp
    src/cli/commands.cpp
)

# Header files
set(HEADERS
    src/core/package.hpp
    src/core/version.hpp
    src/core/dependency.hpp
    src/core/logger.hpp
    src/resolver/resolver.hpp
    src/resolver/greedy.hpp
    src/resolver/backtrack.hpp
    src/resolver/graph.hpp
    src/sources/source.hpp
    src/sources/pypi.hpp
    src/sources/npm.hpp
    src/sources/system.hpp
    src/sources/local.hpp
    src/installer/installer.hpp
    src/installer/plan.hpp
    src/installer/state.hpp
    src/installer/lockfile.hpp
    src/installer/venv.hpp
    src/installer/integrity.hpp
    src/network/http_client.hpp
    src/network/cache.hpp
    src/cli/commands.hpp
    src/json.hpp
)

# Create executable
add_executable(dpm ${SOURCES} ${HEADERS})

# Link libraries
target_link_libraries(dpm 
    ${CURL_LIBRARIES}
)

target_include_directories(dpm PRIVATE
    ${CURL_INCLUDE_DIRS}
)

# Install target
install(TARGETS dpm DESTINATION bin)

