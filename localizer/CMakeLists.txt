cmake_minimum_required(VERSION 3.0.2)
project(perceptive_eye)

set(CMAKE_C_FLAGS "-pthread -std=gnu99 -Wall -O2 -g")
set(CMAKE_CXX_FLAGS "-pthread -std=c++11 -Wall -O2 -g")
add_subdirectory(cc)
