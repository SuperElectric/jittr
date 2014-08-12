# find_package(Glog REQUIRED)
# message(STATUS "glog libs: " ${GLOG_LIBRARIES})
# find_library(CERES_LIBRARY NAMES ceres)  # finds (hopefully) libceres.a 
# message(STATUS "found ceres at " ${CERES_LIBRARY})
find_package(Ceres REQUIRED)
message(STATUS "ceres include dirs: " ${CERES_INCLUDE_DIRS})
message(STATUS "ceres libs: " ${CERES_LIBRARIES})
find_package (Gflags REQUIRED)

# There is no CMake module for ceres, so can't find_package() it.

include_directories (
  ${PROJECT_SOURCE_DIR}/include 
  /usr/include/eigen3 
  ${CERES_INCLUDE_DIRS} 
  ${GLOG_INCLUDE_DIRS}
  ${gflags_INCLUDE_DIR}) 

message(STATUS "project source dir was " ${PROJECT_SOURCE_DIR})

add_library (helloworld SHARED hello_world.cpp)

add_executable (hello_world hello_world_main.cpp) 

# Link the executable to the Hello library, ceres.

#target_link_libraries (hello_world helloworld ${GLOG_LIBRARIES} ${CERES_LIBRARY})
target_link_libraries (hello_world helloworld ${CERES_LIBRARIES} gflags)
