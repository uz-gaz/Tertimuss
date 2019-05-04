# Project performance optimizations
In this document will be explained the different performance optimizations done to the framework to improve the execution
time and decrease the memory usage.

## Profiled versions test environment
All the profiles was done in a Desktop PC with the next characteristics:
- CPU: Intel Pentium E5700 dual core 3.00 GHz, FSB: 800 MHz (FSB bottle neck the RAM frequency)
- RAM: 2 slots of 4 GB (total 8 GB) at 1600 MHz
- GRAPHIC CARD: Nvidia GT 440 (GV-N440D3-1GI), 1 GB of DDR3 memory at 1800 MHz, 96 processing cores at 830 MHz
- HDD: Seagate Barracuda ST1000DM010, 7200 RPM, SATA: 3.0
- OS: Debian GNU/Linux 9.9 (stretch) 64 bits

# Matlab version
The first version, and original, was the Matlab version, in this version, the only parameter measured was the execution time
in a simulation equal to global_edf_affinity_scheduler_test.py and it was 200 seconds of execution time in Matlab 2019a.

# Embedded system laboratory release version
This version, was the release done for the subject laboratory of embedded system done on day 04/04/2019 and corresponds
with the commit 9f8e1631ed63dd190f1e68d132959aadf82e1ca3 in master.

## Improvements
This versions have got a lot of improvements compared to the Matlab version. First of all, the programing language change,
second a code refactoring to accomplish the less matrix operations possible and to improve floating-point operations precision.
Third, the Scipy library usage to improve matrix operations, because with the version of anaconda used in this project
(referenced in the file README.md of the root), Scipy provides a backend of MKL (https://software.intel.com/en-us/mkl)
for the matrix operations. It uses the multimedia extensions (sse and avx) and the multiprocessing, but only when the matrix
are of types floating point of 32 bits or 64 bits. No acceleration is done for integer or other floating points size as
demonstrated in the file /tests/performance/types_performance.py.

## Profiling
The profiling was done with the execution of the test global_edf_affinity_scheduler_test.py.
The time profiling was stored in the file ./profiling/eslr_gedf_a.pstat.