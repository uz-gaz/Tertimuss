# Simulation result analyzing

This section explains how to analyze the result of a simulation. First it explains the simulation output format and
later it presents the offered simulation tools to analyze the output.

## Simulation output description

Every simulation executed with tertimuss returns a RawSimulationResult instance (tertimuss.simulation_lib.simulator).

The class RawSimulationResult has the following properties:

- have_been_scheduled: This property is True if the scheduler agrees to schedule the task set in the provided system
- scheduler_acceptance_error_message: This property only will take a value if have_been_scheduled is False. It contains
  the scheduler's reason for not scheduling the task set in the provided system.
- job_sections_execution: This property contains the list of jobs executed by each core
- cpus_frequencies: This property contains the list of CPU frequencies used by each core
- scheduling_points: This property contains the timestamps of the dynamic component of the scheduler invocation
- temperature_measures: This property contains a list with the evolution of the processors' temperature
- hard_real_time_deadline_missed_stack_trace: This property only takes value if the system misses a hard real-time
  deadline. It contains a snapshot of the system when the deadline miss happens
- memory_usage_record: This property has a record of the memory usage in bytes

## Out of the box tools to analyze simulation output

Tertimuss provides some out of the box tools to analyze simulation output. All of them are located in the package
tertimuss.analysis. They are the following:

- deadline misses: It analyzes the number of deadline misses dividing it in several categories.
- non preemptive task retry: It analyzes the number of times non-preemptive tasks were preempted, so their execution had
  to restart dividing it in several categories.
- preemptions and migrations: It analyze the number of preemptions and migrations dividing it in several categories.

## Out of the box tools to visualize simulation output

Tertimuss provides some tools to visualize simulation output. All of them are located in the package
tertimuss.visualization. They are the following:

- assignation: It visualizes the assignation of tasks or jobs to cores over time.
- execution: It visualizes the execution of tasks or jobs over time.
- accumulate execution: It visualized the accumulated execution time of each task or job in each core.
- frequency evolution: It visualizes the evolution of the frequency in each core.
- component hotspots evolution: It visualizes the temperature of the hottest point in each component of the processor
  (cores and board) over time.
- processor temperature evolution: It visualizes the evolution of the temperature in the processor over time.
