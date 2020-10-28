from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from typing import Optional

# https://site.ieee.org/tcrts/education/terminology-and-notation/
class DeadlineCriteria(Enum):
    HARD_RT = auto()  # Hard real time criteria. If a job with this criteria miss the deadline, the simulation will
    # be stopped
    FIRM_RT = auto()  # Firm real time criteria. If a job with this criteria miss the deadline, the simulation will
    # continue, but the scheduler won't be able to continue the execution of the task
    SOFT_RT = auto()  # Soft real time criteria. If a task with this criteria miss the deadline, the simulation will
    # continue, and the scheduler will be able to continue the execution of the task


@dataclass
class Task(object):
    """
    Task specification
    """
    # Task id
    task_id: int

    # Task worst case execution time in cycles
    c: int

    # Deadline criteria
    deadline_criteria: DeadlineCriteria

    # Energy consumption associated with the task
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

    # Deadline criteria
    deadline_criteria: DeadlineCriteria = DeadlineCriteria.HARD_RT


@dataclass
class AperiodicTask(Task):
    """
    Aperiodic task specification
    """
    # Task arrive time
    a: float

    # Task deadline time
    d: float

    # Deadline criteria
    deadline_criteria: DeadlineCriteria = DeadlineCriteria.SOFT_RT


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
