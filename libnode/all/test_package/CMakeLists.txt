cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES CXX)

find_package(libnode REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE libnode::libnode)
