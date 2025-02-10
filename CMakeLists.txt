# Minimum CMake version required
cmake_minimum_required(VERSION 3.10)

# Project name
project(EchoCash)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)

# Set the path for NCNN source files (adjust if needed)
set(NCNN_PATH "/path/to/ncnn") # Change this to the location of your ncnn source files

# Add source files for your project
set(SOURCE_FILES
    src/main.cpp
    src/other_file.cpp
    # Add any other source files here
)

# Include directories (add the path to the NCNN headers if necessary)
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${NCNN_PATH}/src
)

# Add executable
add_executable(echocash ${SOURCE_FILES})

# Add the path for the NCNN library (for linking)
link_directories(${NCNN_PATH}/lib)

# Link to the NCNN library
target_link_libraries(echocash
    ncnn
)

# For Emscripten WebAssembly target
if(EMSCRIPTEN)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s USE_PTHREADS=1 -s WASM=1 -s MODULARIZE=1 -s EXPORT_NAME='createEchoCash'")
    set(CMAKE_EXECUTABLE_SUFFIX ".html")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s ALLOW_MEMORY_GROWTH=1 -s DISABLE_EXCEPTION_CATCHING=0")

    # Define output directory for wasm files
    set(OUTPUT_DIR ${CMAKE_BINARY_DIR}/deploy)

    # Ensure deployment directory exists
    file(MAKE_DIRECTORY ${OUTPUT_DIR})

    # Copy necessary files for deployment
    add_custom_command(TARGET echocash POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:echocash> ${OUTPUT_DIR}/echocash.js
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/src ${OUTPUT_DIR}/src
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/index.html ${OUTPUT_DIR}/index.html
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/style.css ${OUTPUT_DIR}/style.css
    )
endif()

# Optionally print some helpful information
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "CMake Version: ${CMAKE_VERSION}")
message(STATUS "Project: ${PROJECT_NAME}")

