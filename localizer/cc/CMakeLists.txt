find_package(OpenCV REQUIRED)
include_directories("-I/usr/local/include/chilitags")
link_directories("-L/usr/local/lib -lchilitags.so")

add_library(chili SHARED chilitags.cc)
target_link_libraries(chili ${OpenCV_LIBS} chilitags)
