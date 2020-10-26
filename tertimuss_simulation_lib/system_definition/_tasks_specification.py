from dataclasses import dataclass
from typing import List

from typing import Optional


@dataclass
class Task(object):
    """
    Task specification
    """
    # Task id
    task_id: int

    # Task worst case execution time in cycles
    c: int

    # Energy consumption
    e: Optional[float]


@dataclass
class PeriodicTask(Task):
    """
    Periodic task specification
    """
    # Task period in seconds
    t: float

    # Task deadline in seconds
    d: float


@dataclass
class AperiodicTask(Task):
    """
    Aperiodic task specification
    """
    # Task arrive time
    a: float

    # Task deadline time
    d: float


@dataclass
class TaskSet(object):
    """
    Group of tasks
    """
    # List of periodic tasks
    periodic_tasks: List[PeriodicTask]

    # List of aperiodic tasks
    aperiodic_tasks: List[AperiodicTask]


@dataclass
class Job(object):
    """
    Task specification
    """
    # Task id to which the job belongs
    task_id: int

    # Job remaining cycles
    r: int

    # Job arrive time
    a: float

    # Job deadline time
    d: float
