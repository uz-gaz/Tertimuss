# Scheduling algorithm specification

The scheduling algorithm is the primary focus of tertimuss. This section describes how to define a new scheduling algorithm and the scheduling algorithms provided out of the box.

## Scheduling algorithms types

In the current version of tertimuss all schedulers are implemented in a centralized way. That means that the scheduler can view the state of all cores and can change any executed task at any time it wants to. As a restriction, all processors must synchronize their clocks, so they must share the same frequency.  
A future version of tertimuss will allow the implementation of distributed schedulers.

## Out of the box scheduling algorithms provided

The following algorithms are included in tertimuss:

- ALECS: Allocation and Execution Control Scheduler
- CALECS: Clustered Allocation and Execution Control Scheduler
- RUN: Reduction to Uniprocessor Scheduler
- G-EDF: Global Earliest Deadline First Scheduler

## How to define a new centralized scheduling algorithm

To define a new centralized scheduling algorithm, a class that inherits from CentralizedScheduler has to be declared.

Also, it has to implement the following functions (they are described in the next sub-section):  
- check_schedulability
- offline_stage
- schedule_policy
- on_major_cycle_start
- on_jobs_activation
- on_jobs_deadline_missed
- on_job_execution_finished


The implemented schedulers there are the following approaches:  
- event-driven: The dynamic component of the scheduler activated only by system events
- quantum-based: The dynamic component of the scheduler is activated only from the previous invocation to it through a quantum
- hybrid: An hybrid approach between event-driven and quantum-based

### Example: Implementing simple global earliest deadline first scheduler

This section shows a simple global earliest deadline first scheduler implementation. To keep things simple, it won't take
in account affinity, so it only takes care of executing the tasks with the lowest deadline.  
Also, to reduce the complexity of the implementation, it is event-driven.

```python
from typing import Dict, Optional, Set, List, Tuple

from tertimuss.simulation_lib.schedulers_definition import CentralizedScheduler
from tertimuss.simulation_lib.system_definition import Processor, Environment, TaskSet


class SimpleGlobalEarliestDeadlineFirstScheduler(CentralizedScheduler):
    def __init__(self):
        """
        Create a simple global EDF scheduler instance
        """
        super().__init__(False)
        self.__m = 0
        self.__tasks_relative_deadline: Dict[int, float] = {}
        self.__active_jobs_priority: Dict[int, float] = {}

    def check_schedulability(self, processor_definition: Processor, environment_specification: Environment,
                             task_set: TaskSet) -> [bool, Optional[str]]:
        """
        Return true if the scheduler can be able to schedule the system. In negative case, it can return a reason.
        In example, an scheduler that only can work with periodic tasks with phase=0, can return
         [false, "Only can schedule tasks with phase=0"]
    
        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        return True, None


    def offline_stage(self, processor_definition: Processor, environment_specification: Environment,
                      task_set: TaskSet) -> int:
        """
          Method to implement with the offline stage scheduler tasks
    
          :param environment_specification: Specification of the environment
          :param processor_definition: Specification of the cpu
          :param task_set: Tasks in the system
          :return CPU frequency
          """
        m = len(processor_definition.cores_definition)
    
        clock_available_frequencies = Set.intersection(*[i.core_type.available_frequencies for i
                                                         in processor_definition.cores_definition.values()])
    
        self.__m = m
    
        self.__tasks_relative_deadline = {i.identifier: i.relative_deadline for i in
                                          task_set.periodic_tasks + task_set.aperiodic_tasks +
                                          task_set.sporadic_tasks}
    
        return max(clock_available_frequencies)
    
    
    def schedule_policy(self, global_time: float, active_jobs_id: Set[int], jobs_being_executed_id: Dict[int, int],
                        cores_frequency: int, cores_max_temperature: Optional[Dict[int, float]]) \
        -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police
        
        :param global_time: Time in seconds since the simulation starts
        :param jobs_being_executed_id: Ids of the jobs that are currently executed on the system. The dictionary has as
         key the CPU id (it goes from 0 to number of CPUs - 1), and as value the job id.
        :param active_jobs_id: Identifications of the jobs that are currently active
         (look in :ref:..system_definition.DeadlineCriteria for more info) and can be executed.
        :param cores_frequency: Frequencies of cores on the scheduler invocation in Hz.
        :param cores_max_temperature: Max temperature of each core. The dictionary has as
         key the CPU id, and as value the temperature in Kelvin degrees.
        :return: Tuple of [
         Jobs CPU assignation. The dictionary has as key the CPU id, and as value the job id,
         Cycles to execute until the next invocation of the scheduler. If None, it won't be executed until a system
         event trigger its invocation,
         CPU frequency. If None, it will maintain the last used frequency (cores_frequency)
        ]
        """
        # The priority of the tasks must be inverse to the deadline
        tasks_that_can_be_executed: List[Tuple[int, float]] = sorted([i for i in self.__active_jobs_priority.items()],
                                                                     key=lambda j: j[1])
        
        # All tasks will be executed
        tasks_to_execute = {k: i for (i, j), k in zip(tasks_that_can_be_executed, range(self.__m))}
        
        return tasks_to_execute, None, None
    
    
    def on_major_cycle_start(self, global_time: float) -> bool:
        """
        On new major cycle start event
    
        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return True
    
    
    def on_jobs_activation(self, global_time: float, activation_time: float,
                           jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
        """
        Method to implement with the actual on job activation scheduler police.
        This method is the recommended place to detect the arrival of an aperiodic or sporadic task.
    
        :param jobs_id_tasks_ids: List[Identification of the job that have been activated,
         Identification of the task which job have been activated]
        :param global_time: Actual time in seconds since the simulation starts
        :param activation_time: Time where the activation was produced (It can be different from the global_time in the
         case that it doesn't adjust to a cycle end)
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        self.__active_jobs_priority.update(
            {i: self.__tasks_relative_deadline[j] + activation_time for i, j in jobs_id_tasks_ids})
        return True
    
    
    def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
        """
         Method to implement with the actual on aperiodic arrive scheduler police
    
         :param jobs_id: Identification of the jobs that have missed the deadline
         :param global_time: Time in seconds since the simulation starts
         :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
         """
        for i in jobs_id:
            del self.__active_jobs_priority[i]
        return True
    
    
    def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
    
        :param jobs_id: Identification of the job that have finished its execution
        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        for i in jobs_id:
            del self.__active_jobs_priority[i]
        return True
```

First, the function __check_schedulability__ checks if the schedule is capable of schedule the task set in the system provided.  
In this example, the implemented scheduler accepts all kind of task sets and systems, however in the case that the scheduler only could handle some types of systems (i.e. if only could handle soft real-time tasks),
and the restrictions have not met this function must return False and an explanatory message for the user.

The function __offline_stage__ must run the static operations of the schedulers and set a frequency for the processors.
In this example, the implementation take always the maximum available frequency.

The function __schedule_policy__ must run the dynamic operations of the scheduler. Its functions are to select the tasks to execute and the frequency of the processor until the next invocation, and set when the next invocation will take place.
If the scheduler is event-driven, like this example, the number of cycles to execute until the next invocation can be __None__, which means that the scheduler won't take place until a handled event call it. If the frequency value is None, it will remain the last one used.
In this example, the jobs with the nearest deadline are executed, and booth the frequency and the number of cycles until the next invocation are set to __None__. 

The function __on_major_cycle_start__ is invoked when a major cycle start. If the scheduler returns True, the __schedule_policy__ function is called this same cycle.
In this example, it will return true because it is an event-driven scheduler.

The function __on_jobs_activation__ is invoked when a new job is activated. If the scheduler returns True, the __schedule_policy__ function is called this same cycle.
In this example, it will return true because it is an event-driven scheduler.

The function __on_job_execution_finished__ is invoked when a job finished its execution. If the scheduler returns True, the __schedule_policy__ function is called this same cycle.
In this example, it will return true because it is an event-driven scheduler.

The function __on_jobs_deadline_missed__ is invoked when a job miss its deadline. If the scheduler returns True, the __schedule_policy__ function is called this same cycle.
In this example, it will return true because it is an event-driven scheduler.
