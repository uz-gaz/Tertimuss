"""
==========================================
Simulation specification
==========================================

This module allow to specify the simulation properties
"""
from ._processor_specification import CoreEnergyConsumption, CoreTypeDefinition, BoardDefinition, CoreDefinition, \
    ProcessorDefinition
from ._environment_specification import EnvironmentSpecification
from ._tasks_specification import Criticality, PreemptiveExecution, AbstractExecutionTimeDistribution, \
    AlwaysWorstCaseExecutionTimeDistribution, Task, PeriodicTask, AperiodicTask, SporadicTask, TaskSet, Job
