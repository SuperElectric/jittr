find_package(Ceres REQUIRED)
message(STATUS "ceres include dirs: " ${CERES_INCLUDE_DIRS})
message(STATUS "ceres libs: " ${CERES_LIBRARIES})

include_directories (
  ${PROJECT_SOURCE_DIR}/include 
  /usr/include/eigen3 
  ${CERES_INCLUDE_DIRS} 
  ${GLOG_INCLUDE_DIRS}
  ${gflags_INCLUDE_DIR}) 

message(STATUS "project source dir was " ${PROJECT_SOURCE_DIR})

add_executable (find_cam find_cam.cpp) 

target_link_libraries (find_cam ${CERES_LIBRARIES} gflags)
