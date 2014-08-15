# Put CMake directives here
cmake_minimum_required (VERSION 2.6) 
project (find_cam)

# Where to look for FindXXXX.cmake files
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR}/cmake_modules/)
message(STATUS "cmake_module_path: " ${CMAKE_MODULE_PATH})

# Where to put programs
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)  # build/bin

# Where to put built libraries
set(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)  # build/lib

add_subdirectory (src)
