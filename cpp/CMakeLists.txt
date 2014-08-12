# Put CMake directives here
cmake_minimum_required (VERSION 2.6) 
project (jittr)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR}/cmake_modules/)
message(STATUS "cmake_module_path: " ${CMAKE_MODULE_PATH})
add_subdirectory (src)
