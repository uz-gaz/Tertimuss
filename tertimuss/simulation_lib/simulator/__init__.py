"""
===================
Scheduler simulator
===================

Provide the utilities to simulate the scheduler behaviour

This module provides the following functions:
- :function:`.execute_scheduler_simulation_simple`
- :function:`.execute_scheduler_simulation`

It also exposes the following classes related with the previous functions:
- :class:`.JobSectionExecution`
- :class:`.CPUUsedFrequency`
- :class:`.SimulationStackTraceHardRTDeadlineMissed`
- :class:`.RawSimulationResult`
- :class:`.SimulationConfiguration`
"""
from ._simulation_result import JobSectionExecution, CPUUsedFrequency, SimulationStackTraceHardRTDeadlineMissed, \
    RawSimulationResult
from ._system_simulator import SimulationConfiguration, execute_scheduler_simulation_simple, \
    execute_scheduler_simulation
