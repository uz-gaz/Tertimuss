# Project performance optimizations
In this document, will be explained the different performance optimizations done to the framework to improve the execution
time and decrease the memory usage

# Matlab version
The first version, and original, was the Matlab version, in this version, the only parameter measured was the execution time
in a simulation equal to global_edf_affinity_scheduler_test.py and it was 200 seconds of execution time.

# Embedded system laboratory release version
This version, was the release done for the subject laboratory of embedded system done on day 04/04/2019 and corresponds
with the commit 9f8e1631ed63dd190f1e68d132959aadf82e1ca3 in master.

## Improvements
This versions have got a lot of improvements, first of all the change of programing language, second a refactorization
of the code to acomplish the less matrix operations possible and in other way, other refactaro to improve floating-point results after operations,
third the use of the scipy library to improve matrix operations. With the version of anaconda used (referenced in the file README.md of the root), scipy provide
a backend of MKL (https://software.intel.com/en-us/mkl) for the operations, it uses the multimedia extensions (sse and avx) and the multiprocessing to improve the
matrix operations, but it is only used when  the matrix are of types floating point of 32 bits o 64 bits, no acceleration is done
for integer or other floating points size.

## Profiling
Profiling eslr_gedf_a.pstat