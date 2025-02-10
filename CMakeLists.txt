cmake_minimum_required(VERSION 3.0)

project(EchoCash)

set(CMAKE_CXX_STANDARD 11)

# WebAssembly specific settings
set(CMAKE_TOOLCHAIN_FILE /home/runner/work/EchoCash/EchoCash/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake)

# Enable Pthreads support for WebAssembly
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

# Set the name for the export module (required when using MODULARIZE with Pthreads)
set(EXPORT_NAME "EchoCash")

# Add source files
add_executable(echocash main.cpp)

# Link to necessary libraries
target_link_libraries(echocash PRIVATE -s USE_PTHREADS=1 -s EXPORT_NAME=${EXPORT_NAME} -s ALLOW_MEMORY_GROWTH=1)

# If you have other required dependencies, link them here
# target_link_libraries(echocash PRIVATE other-libraries)

# Set output folder
set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/build)

# Optionally, install the generated files if needed
# install(TARGETS echocash DESTINATION /usr/local/bin)
