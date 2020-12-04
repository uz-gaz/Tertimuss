"""
The different task requirements and restrictions have been inspired by
https://site.ieee.org/tcrts/education/terminology-and-notation/

Some of the definitions have been taken from the same page
"""
import abc
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List

from typing import Optional


class Criticality(Enum):
    """
    A property specifying the consequence for the whole system of missing the task timing constraints. This property is
     typically specified as a set of task classes
    """
    HARD = auto()  # A task is said to be hard if missing the timing constraint of any of its job may jeopardize the
    # correct behavior of the entire system. If a job with this criteria miss the timing constraint, the simulation will
    # be stopped
    FIRM = auto()  # A task is said to be firm if missing a timing constraint does not jeopardize the correct system
    # behavior but it is completely useless for the system. If a job with this criteria miss the deadline, the
    # simulation will continue, but the scheduler won't be able to continue the execution of the task
    SOFT = auto()  # A task is said to be soft if missing a timing constraint does not jeopardize the correct system
    # behavior and has a still a reduced value for the system. If a task with this criteria miss the deadline, the
    # simulation will continue, and the scheduler will be able to continue the execution of the task


class PreemptiveExecution(Enum):
    """
    Possibility of interrupting the execution of a task (in favor of another computational activity) and resume it at a
    later time
    """
    FULLY_PREEMPTIVE = auto()  # A task is fully preemptive if it can be interrupted anytime and anywhere during its
    # execution
    NON_PREEMPTIVE = auto()  # A task is non preemptive if it cannot be interrupted during its execution


class AbstractExecutionTimeDistribution(object, metaclass=abc.ABCMeta):
    """
    Abstract probability distribution of task execution times over all possible input data
    """

    @abc.abstractmethod
    def generate_execution_time(self, best_case_execution_time: int, worst_case_execution_time: int) -> int:
        """
        Generate one execution time
        :param best_case_execution_time: The shortest execution time needed by a processor to complete the task without
        interruption over all possible input data in cycles
        :param worst_case_execution_time: The longest execution time needed by a processor to complete the task without
         interruption over all possible input data in cycles
        :return: The execution time generated
        """
        pass


class AlwaysWorstCaseExecutionTimeDistribution(AbstractExecutionTimeDistribution):
    """
    Execution time distribution where the execution time is always the worst case
    """

    def generate_execution_time(self, best_case_execution_time: int, worst_case_execution_time: int) -> int:
        """
        Generate one execution time
        :param best_case_execution_time: The shortest execution time needed by a processor to complete the task without
        interruption over all possible input data in cycles
        :param worst_case_execution_time: The longest execution time needed by a processor to complete the task without
         interruption over all possible input data in cycles
        :return: The execution time generated
        """
        return worst_case_execution_time


@dataclass(frozen=True)
class Task(object):
    """
    Task specification
    """
    # Identification of the task
    identification: int

    # The longest execution time needed by a processor to complete the task without interruption over all possible input
    # data in cycles
    worst_case_execution_time: int

    # The longest interval of time within which any job should complete its execution
    relative_deadline: float

    # The shortest execution time needed by a processor to complete the task without
    # interruption over all possible input data in cycles
    best_case_execution_time: Optional[int]

    # Probability distribution of task execution times over all possible input data
    execution_time_distribution: Optional[AbstractExecutionTimeDistribution]

    # Maximum memory space required to run the task in Bytes
    memory_footprint: Optional[int]

    # A number expressing the relative importance of a task with respect to the other tasks in the system
    priority: Optional[int]

    # Preemptive execution
    preemptive_execution: PreemptiveExecution

    # Deadline criteria
    deadline_criteria: Criticality

    # Energy consumption of each job of the task in Jules
    energy_consumption: Optional[float]


@dataclass(frozen=True)
class PeriodicTask(Task):
    """
    A task in which jobs are activated at regular intervals of time, such that the activation of consecutive jobs is
    separated by a fixed interval of time, called the task period
    """
    # The time at which the first job is activated
    phase: Optional[float]

    # Fixed separation interval between the activation of any two consecutive jobs
    period: float


@dataclass(frozen=True)
class AperiodicTask(Task):
    """
    Aperiodic task specification
    """
    pass


@dataclass(frozen=True)
class SporadicTask(Task):
    """
    Sporadic task specification
    """
    # Minimum separation interval between the activation of consecutive jobs
    minimum_interarrival_time: float


@dataclass(frozen=True)
class TaskSet(object):
    """
    Group of tasks
    """
    # List of periodic tasks
    periodic_tasks: List[PeriodicTask]

    # List of aperiodic tasks
    aperiodic_tasks: List[AperiodicTask]

    # List of sporadic tasks
    sporadic_tasks: List[SporadicTask]


@dataclass  # (frozen=True)
class Job(object):
    """
    Task specification
    """
    # Identification of the job
    identification: int

    # Task to which the job belongs
    task: Task

    # Job arrive time
    activation_time: float

    # The time at which the job should complete its execution
    absolute_deadline: float = field(init=False)

    # The execution time of the job
    execution_time: int = field(init=False)

    def __post_init__(self):
        self.absolute_deadline = self.activation_time + self.task.relative_deadline
        self.execution_time = self.task.execution_time_distribution.generate_execution_time(
            self.task.best_case_execution_time,
            self.task.worst_case_execution_time) if self.task.execution_time_distribution is not None \
            else self.task.worst_case_execution_time
