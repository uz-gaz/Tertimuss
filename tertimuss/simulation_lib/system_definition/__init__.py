"""
==========================================
Simulation specification
==========================================

This module allows to specify the simulation properties

This module exposes the following classes:
- :class:`.EnergyConsumption`
- :class:`.CoreModel`
- :class:`.Board`
- :class:`.Core`
- :class:`.Processor`
- :class:`.Environment`
- :class:`.Criticality`
- :class:`.PreemptiveExecution`
- :class:`.ExecutionTimeDistribution`
- :class:`.ETDAlwaysWorstCase`
- :class:`.Task`
- :class:`.PeriodicTask`
- :class:`.AperiodicTask`
- :class:`.SporadicTask`
- :class:`.TaskSet`
- :class:`.Job`
"""
from ._processor_specification import EnergyConsumption, CoreModel, Board, Core, \
    Processor
from ._environment_specification import Environment
from ._tasks_specification import Criticality, PreemptiveExecution, ExecutionTimeDistribution, \
    ETDAlwaysWorstCase, Task, PeriodicTask, AperiodicTask, SporadicTask, TaskSet, Job
