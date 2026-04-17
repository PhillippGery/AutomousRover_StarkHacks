#######################################################################################
cmake_minimum_required(VERSION 3.8)
#######################################################################################
project(l3xz_sweep_scanner)
set(L3XZ_SWEEP_SCANNER_TARGET ${PROJECT_NAME}_node)
#######################################################################################
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Werror -Wextra -Wpedantic)
endif()
#######################################################################################
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
#######################################################################################
include_directories(
  include
)
#######################################################################################
add_subdirectory(external/libsweep/current)
add_executable(${L3XZ_SWEEP_SCANNER_TARGET}
  src/main.cpp
  src/SweepScannerNode.cpp
)
target_link_libraries(${L3XZ_SWEEP_SCANNER_TARGET} sweep)
#######################################################################################
target_compile_features(${L3XZ_SWEEP_SCANNER_TARGET} PRIVATE cxx_std_17)
ament_target_dependencies(${L3XZ_SWEEP_SCANNER_TARGET} rclcpp sensor_msgs)
#######################################################################################
install(TARGETS
  ${L3XZ_SWEEP_SCANNER_TARGET}
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)
#######################################################################################
ament_package()
#######################################################################################
