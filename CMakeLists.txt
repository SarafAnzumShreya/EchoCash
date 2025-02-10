cmake_minimum_required(VERSION 3.14)
project(EchoCash)

# Set Emscripten toolchain
if(NOT EMSCRIPTEN)
    message(FATAL_ERROR "Emscripten toolchain not found! Make sure you run 'source emsdk/emsdk_env.sh'")
endif()

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)

# Include NCNN
set(NCNN_DIR ${CMAKE_SOURCE_DIR}/ncnn)  # Adjust this if NCNN is in a different path
include_directories(${NCNN_DIR}/include)
link_directories(${NCNN_DIR}/lib)

# Define the executable
set(SRC_FILES main.cpp)  # Replace with your actual source files
add_executable(echocash ${SRC_FILES})

# Link against NCNN
target_link_libraries(echocash ncnn)

# WebAssembly settings
set(CMAKE_EXECUTABLE_SUFFIX ".html")  # Output an HTML file
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s USE_PTHREADS=1 -s TOTAL_MEMORY=512MB -s ALLOW_MEMORY_GROWTH=1 -s EXPORT_ALL=1 -s MODULARIZE=1 -s WASM=1")

# Output the WebAssembly and JavaScript bindings
set_target_properties(echocash PROPERTIES OUTPUT_NAME "model")
