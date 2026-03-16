cmake_minimum_required(VERSION 3.31.0)
set(ROOT "${CMAKE_CURRENT_LIST_DIR}")
project ( vecjoin-cpu )

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable AVX2 + FMA intrinsics (Zen3)
add_compile_options(-mavx2 -mfma -O3)


FIND_PACKAGE( OpenMP REQUIRED)
if(OPENMP_FOUND)
message("OPENMP FOUND")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

# OpenBLAS for SGEMM
find_package(BLAS REQUIRED)
message(STATUS "BLAS libraries: ${BLAS_LIBRARIES}")

file(GLOB SRC
"*.cpp"
)



add_executable(vecjoin-cpu main.cpp ${SRC})
target_link_libraries(vecjoin-cpu ${BLAS_LIBRARIES})