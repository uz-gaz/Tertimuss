__Work in progress__

## System specification
Here you will express how is your system, so the simulator will behaves accordingly to it.

The same specification can be used with several schedulers to compare them.

This specification is formed by four elements:

## Task set specification
In the task set specification you will specify how are the tasks in your system. Even you can specify how are the jobs in it.

The notation in the tasks specification tries to follow as possible the notation proposed by the [IEEE Technical Committee on Real-Time Systems](https://site.ieee.org/tcrts/education/terminology-and-notation/). Most of the definitions are directly from there.

The tasks can be of three different types, periodics (PeriodicTask), aperiodics (AperiodicTask) and sporadics (SporadicTask).

All of them share some properties that we will define now:

- identification: An unique identification for the task in the system
- worst case execution time: The longest execution time needed by a processor to complete the task without interruption over all possible input data in cycles
- relative_deadline: The longest interval of time within which any job should complete its execution
- best case execution time: The shortest execution time needed by a processor to complete the task without interruption over all possible input data in cycles
- execution time distribution: Probability distribution of task execution times over all possible input data
- memory footprint: Maximum memory space required to run the task in Bytes
- priority: A number expressing the relative importance of a task with respect to the other tasks in the system
- preemptive execution: Establishes if the task can be preempted (fully preemptive) or it can't be (non preemptive). Partially preemptive tasks are not allowed in this model
- deadline criteria: A property specifying the consequence for the whole system of missing the task timing constraints

In the case of periodic tasks, them have the following properties too:

- phase: The time at which the first job is activated
- period: Fixed separation interval between the activation of any two consecutive jobs

In the case of sporadic tasks, them have the following property too:
minimum interarrival time: Minimum separation interval between the activation of consecutive jobs

Lets take a look of a 

### Jobs specification

## Processor specification

## Environment specification