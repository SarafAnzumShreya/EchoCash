# Minimum version of CMake required
cmake_minimum_required(VERSION 3.10)

# Project name
project(EchoCash)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check if Emscripten is being used
if(EMSCRIPTEN)

    # Set the CMake flags for building with Emscripten
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s USE_PTHREADS=1 -s WASM=1 -s MODULARIZE=1 -s EXPORT_NAME='createEchoCash'")
    set(CMAKE_EXECUTABLE_SUFFIX ".html")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s ALLOW_MEMORY_GROWTH=1 -s DISABLE_EXCEPTION_CATCHING=0")

    # Define output directory for wasm files
    set(OUTPUT_DIR ${CMAKE_BINARY_DIR}/deploy)

    # Ensure deployment directory exists
    file(MAKE_DIRECTORY ${OUTPUT_DIR})

endif()

# Add source directory
include_directories(${CMAKE_SOURCE_DIR}/src)

# Add the executable
add_executable(echocash main.cpp)

# Specify any libraries you need to link against
# target_link_libraries(echocash <libraries>)

# After defining the target, add the custom command
add_custom_command(TARGET echocash POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:echocash> ${OUTPUT_DIR}/echocash.js
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/src ${OUTPUT_DIR}/src
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/index.html ${OUTPUT_DIR}/index.html
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/style.css ${OUTPUT_DIR}/style.css
)
