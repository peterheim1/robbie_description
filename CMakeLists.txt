cmake_minimum_required(VERSION 3.10.2)
project(robbie_description)
find_package(ament_cmake REQUIRED)

ament_package()

install(DIRECTORY launch config meshes urdf DESTINATION share/${PROJECT_NAME})
