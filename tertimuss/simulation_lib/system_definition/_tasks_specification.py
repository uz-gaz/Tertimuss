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
    HARD = auto()
    """A task is said to be hard if missing the timing constraint of any of its job may jeopardize the
    correct behavior of the entire system. If a job with this criteria miss the timing constraint, the simulation will
    be stopped"""

    FIRM = auto()
    """A task is said to be firm if missing a timing constraint does not jeopardize the correct system
    behavior but it is completely useless for the system. If a job with this criteria miss the deadline, the
    simulation will continue, but the scheduler won't be able to continue the execution of the task"""

    SOFT = auto()
    """A task is said to be soft if missing a timing constraint does not jeopardize the correct system
    behavior and has a still a reduced value for the system. If a task with this criteria miss the deadline, the
    simulation will continue, and the scheduler will be able to continue the execution of the task"""


class PreemptiveExecution(Enum):
    """
    Possibility of interrupting the execution of a task (in favor of another computational activity) and resume it at a
    later time
    """
    FULLY_PREEMPTIVE = auto()
    """A task is fully preemptive if it can be interrupted anytime and anywhere during its execution"""

    NON_PREEMPTIVE = auto()
    """A task is non-preemptive if it cannot be interrupted during its execution"""


class ExecutionTimeDistribution(object, metaclass=abc.ABCMeta):
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


class ETDAlwaysWorstCase(ExecutionTimeDistribution):
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
    identifier: int
    """A unique identifier for the task in the system"""

    worst_case_execution_time: int
    """The longest execution time needed by a processor to complete the task without interruption over all possible
    input data in cycles"""

    relative_deadline: float
    """The longest interval of time within which any job should complete its execution"""

    best_case_execution_time: Optional[int]
    """The shortest execution time needed by a processor to complete the task without interruption over all possible
    input data in cycles"""

    execution_time_distribution: Optional[ExecutionTimeDistribution]
    """Probability distribution of task execution times over all possible input data"""

    memory_footprint: Optional[int]
    """Maximum memory space required to run the task in Bytes"""

    priority: Optional[int]
    """A number expressing the relative importance of a task with respect to the other tasks in the system"""

    preemptive_execution: PreemptiveExecution
    """Preemptive execution"""

    deadline_criteria: Criticality
    """Deadline criteria"""

    energy_consumption: Optional[float]
    """Energy consumption of each job of the task in Jules"""


@dataclass(frozen=True)
class PeriodicTask(Task):
    """
    A task in which jobs are activated at regular intervals of time, such that the activation of consecutive jobs is
    separated by a fixed interval of time, called the task period
    """
    phase: Optional[float]
    """The time at which the first job is activated"""

    period: float
    """Fixed separation interval between the activation of any two consecutive jobs"""


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
    minimum_interarrival_time: float
    """Minimum separation interval between the activation of consecutive jobs"""


@dataclass(frozen=True)
class TaskSet(object):
    """
    Group of tasks
    """
    periodic_tasks: List[PeriodicTask]
    """List of periodic tasks"""

    aperiodic_tasks: List[AperiodicTask]
    """List of aperiodic tasks"""

    sporadic_tasks: List[SporadicTask]
    """List of sporadic tasks"""

    def tasks(self) -> List[Task]:
        """
        Return the list of tasks

        :return: list of tasks in the task set
        """
        return self.periodic_tasks + self.aperiodic_tasks + self.sporadic_tasks


@dataclass
class Job(object):
    """
    Task specification
    """
    identifier: int
    """A unique identifier of the job in the system"""

    task: Task
    """Task to which the job belongs"""

    activation_time: float
    """Job arrive time"""

    absolute_deadline: float = field(init=False)
    """The time at which the job should complete its execution"""

    execution_time: int = field(init=False)
    """The execution time of the job"""

    def __post_init__(self):
        self.absolute_deadline = self.activation_time + self.task.relative_deadline
        self.execution_time = self.task.execution_time_distribution.generate_execution_time(
            self.task.best_case_execution_time,
            self.task.worst_case_execution_time) if self.task.execution_time_distribution is not None \
            else self.task.worst_case_execution_time
