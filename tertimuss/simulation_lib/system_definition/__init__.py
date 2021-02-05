"""
==========================================
Simulation specification
==========================================

This module allows to specify the simulation properties

This module exposes the following classes:
- :class:`.CoreEnergyConsumption`
- :class:`.CoreTypeDefinition`
- :class:`.BoardDefinition`
- :class:`.CoreDefinition`
- :class:`.ProcessorDefinition`
- :class:`.EnvironmentSpecification`
- :class:`.Criticality`
- :class:`.PreemptiveExecution`
- :class:`.AbstractExecutionTimeDistribution`
- :class:`.AlwaysWorstCaseExecutionTimeDistribution`
- :class:`.Task`
- :class:`.PeriodicTask`
- :class:`.AperiodicTask`
- :class:`.SporadicTask`
- :class:`.TaskSet`
- :class:`.Job`
"""
from ._processor_specification import CoreEnergyConsumption, CoreTypeDefinition, BoardDefinition, CoreDefinition, \
    ProcessorDefinition
from ._environment_specification import EnvironmentSpecification
from ._tasks_specification import Criticality, PreemptiveExecution, AbstractExecutionTimeDistribution, \
    AlwaysWorstCaseExecutionTimeDistribution, Task, PeriodicTask, AperiodicTask, SporadicTask, TaskSet, Job
