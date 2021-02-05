"""
==============================================================
Simulation environment for Real-Time Multiprocessor Schedulers
==============================================================

Tertimuss is an evaluation tool for real-time multiprocessor schedulers. A user-friendly interface makes the scheduler
implementation and evaluation easier. It is primarily designed for tentative design phase of a scheduling algorithm,
where some computer architectural restrictions can be obviated.

Using Tertimuss you can execute simulations using your own scheduler implementation, or one of the RT multiprocessor
schedulers already available in the framework, with a customizable CPU definition as well as a customizable task set.
Task sets can be automatically generated using common task generation algorithms.Tertimuss also integrates tools for
analyzing and representing simulation results.

It contains the following sub-modules:

- :mod:`.simulation_lib`: Set of tools to simulate the behavior of a scheduler in a provided system definition
- :mod:`.analysis`: Set of tools to analyze the result of the simulations
- :mod:`.visualization`: Set of tools to visualize the result of the simulations
- :mod:`.tasks_generator`: Set of tools to automatically generate task-sets

The following libraries are also provided:

- :mod:`.cubed_space_thermal_simulator`: Library to simulate the thermal behavior of a mesh defined by cubes
- :mod:`.tcpn_simulator`: Library to simulate Timed Continuous Petri Nets

"""
