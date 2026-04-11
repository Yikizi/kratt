cmake_minimum_required(VERSION 3.22.1)
project(krattfrontend C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

file(GLOB MICROFRONTEND_C_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/microfrontend/src/*.c"
)

add_library(krattfrontend SHARED
    native-lib.cpp
    ${MICROFRONTEND_C_SOURCES}
)

target_include_directories(krattfrontend PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/microfrontend/include
    ${CMAKE_CURRENT_SOURCE_DIR}/microfrontend/src
)

find_library(log-lib log)

target_link_libraries(krattfrontend
    ${log-lib}
)

target_compile_options(krattfrontend PRIVATE
    -Wno-unused-function
    -Wno-unused-variable
    -Wno-unused-but-set-variable
    -Wno-implicit-function-declaration
    -Wno-incompatible-pointer-types
    -Wno-shift-negative-value
)

# Android 16 (API 36) requires native libraries to be aligned for 16 KB
# memory pages on devices that ship with 16 KB pages enabled (Pixel 8a is one
# of them). Without this flag the loader logs a warning at install time and
# may refuse to load the .so on a future system update.
target_link_options(krattfrontend PRIVATE
    "-Wl,-z,max-page-size=16384"
)
