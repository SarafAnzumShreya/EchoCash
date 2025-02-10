cmake_minimum_required(VERSION 3.10)

# Project name and version
project(CurrencyDetection VERSION 1.0)

# Set the C++ standard to 11 (or higher if needed)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Emscripten-specific settings
if(EMSCRIPTEN)
    # Set the output suffix to .html for a web application
    set(CMAKE_EXECUTABLE_SUFFIX ".html")
    
    # Specify the export name and enable modularization
    set(EXPORT_NAME "createEchoCash")
    set(MODULARIZE 1)

    # Enable WebAssembly and memory growth for better performance
    set(WASM_FLAGS "-s MODULARIZE=1 -s EXPORT_NAME=${EXPORT_NAME} -s WASM=1 -s ALLOW_MEMORY_GROWTH=1 -s USE_PTHREADS=1 -s 'EXTRA_EXPORTED_RUNTIME_METHODS=[\"ccall\", \"cwrap\"]'")

    # Include the directories for the Emscripten toolchain
    include_directories(${EMSCRIPTEN_INCLUDE_DIRS})
    
    # Link Emscripten libraries
    link_directories(${EMSCRIPTEN_LIBRARY_DIRS})

    # Set the output directory for the WebAssembly files
    set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/build)

    # Add the source files (main.cpp and other necessary files)
    add_executable(CurrencyDetection main.cpp)

    # Link Emscripten settings and libraries
    target_link_libraries(CurrencyDetection PRIVATE ${WASM_FLAGS})
endif()

# Standard CMake settings for non-Emscripten environments (optional)
if(NOT EMSCRIPTEN)
    add_executable(CurrencyDetection main.cpp)
endif()

# For building with specific flags or libraries
# target_link_libraries(CurrencyDetection <your-libraries>)
