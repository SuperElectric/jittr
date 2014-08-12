find_package(Glog)
#find_package(ceres)

include_directories (${PROJECT_SOURCE_DIR}/include /usr/include/eigen3 ${GLOG_INCLUDE_DIRS}) 
message(STATUS "project source dir was " ${PROJECT_SOURCE_DIR})

add_library (helloworld SHARED hello_world.cpp)

add_executable (hello_world hello_world_main.cpp) 

# Link the executable to the Hello library, ceres.
find_library(CERES_LIBRARY NAMES ceres)  # finds (hopefully) libceres.a 
# find_library(glog_library NAMES glog)
message(STATUS "glog libs: " ${GLOG_LIBRARIES})
target_link_libraries (hello_world helloworld ${GLOG_LIBRARIES} ${CERES_LIBRARY})

