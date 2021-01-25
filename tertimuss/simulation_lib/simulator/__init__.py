"""
==========================================
Scheduler simulator
==========================================

Provide the utilities to simulate the scheduler behaviour
"""
from ._simulation_result import JobSectionExecution, CPUUsedFrequency, SimulationStackTraceHardRTDeadlineMissed, \
    RawSimulationResult
from ._system_simulator import SimulationOptionsSpecification, execute_scheduler_simulation_simple, \
    execute_scheduler_simulation
