cmake_minimum_required(VERSION 3.0)

project(EchoCash)

set(CMAKE_CXX_STANDARD 11)

# WebAssembly specific settings
set(CMAKE_TOOLCHAIN_FILE /home/runner/work/EchoCash/EchoCash/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake)

# Enable Pthreads support for WebAssembly
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

# Set necessary WebAssembly flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s USE_PTHREADS=1 -s EXPORT_NAME='EchoCash' -s ALLOW_MEMORY_GROWTH=1")

# Set the name for the export module (required when using MODULARIZE with Pthreads)
set(EXPORT_NAME "EchoCash")

# Add source files
add_executable(echocash main.cpp)

# Preload files from the assets directory
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --preload-file ${CMAKE_CURRENT_SOURCE_DIR}/assets@.")

# Link necessary libraries (note that the flags are no longer passed as libraries)
target_link_libraries(echocash PRIVATE)

# Set output folder
set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/build)

# Optionally, install the generated files if needed
# install(TARGETS echocash DESTINATION /usr/local/bin)
