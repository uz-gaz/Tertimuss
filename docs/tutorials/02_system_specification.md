# System specification

The system specification provides all the characteristics that the simulator knows about the system.

The specification is composed of three elements (task set specification, processor specification, and environment
specification) and the same specification can be used with multiple schedulers to compare them.

All classes relatives to system specification are contained in tertimuss.simulation_lib.schedulers_definition package.

## Task set specification

The task set specification specifies how are the tasks and the jobs in the system.

The notation in the specification of the task tries to follow as possible the notation proposed by
the [IEEE Technical Committee on Real-Time Systems](https://site.ieee.org/tcrts/education/terminology-and-notation/).
Most of the definitions are directly from there.

The tasks can be of three different types, periodic (PeriodicTask), aperiodic (AperiodicTask), and sporadic (
SporadicTask).

All of them share the following properties:
- identifier: An unique identifier for the task in the system
- worst-case execution time: The longest execution time needed by a processor to complete the task without interruption
  over all possible input data in cycles
- relative_deadline: The longest interval of time within which any job should complete its execution
- best case execution time: The shortest execution time needed by a processor to complete the task without interruption
  over all possible input data in cycles
- execution time distribution: Probability distribution of task execution times over all possible input data
- memory footprint: Maximum memory space required to run the task in Bytes
- priority: A number expressing the relative importance of a task to the other tasks in the system
- preemptive execution: Establishes if the task can be preempted (fully preemptive), or it can't be (non-preemptive).
  Partially preemptive tasks are not allowed in this model
- deadline criteria: A property specifying the consequence for the whole system of missing the task timing constraints
- energy consumption: Energy consumption of each job of the task in Jules

Only in the case of periodic tasks, they have the following properties too:
- phase: The time at which the first job is activated
- period: Fixed separation interval between the activation of any two consecutive jobs

Only in the case of sporadic tasks, they have the following property too:
- minimum interarrival time: Minimum separation interval between the activation of consecutive jobs

In the case of the job specification (Job), they have the following properties:
- identifier: An unique identifier for the job in the system
- task: Task to which the job belongs
- activation_time: Job arrival time

### Examples

```python
from tertimuss.simulation_lib.system_definition import PeriodicTask, AperiodicTask, SporadicTask, PreemptiveExecution, \
    Criticality, Job, TaskSet

periodic_task_definition = PeriodicTask(identifier=1,
                                        worst_case_execution_time=600,
                                        relative_deadline=1,
                                        best_case_execution_time=None,
                                        execution_time_distribution=None,
                                        memory_footprint=None,
                                        priority=None,
                                        preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                                        deadline_criteria=Criticality.HARD,
                                        energy_consumption=None,
                                        phase=None,
                                        period=1)

aperiodic_task_definition = AperiodicTask(identifier=1,
                                          worst_case_execution_time=600,
                                          relative_deadline=1,
                                          best_case_execution_time=None,
                                          execution_time_distribution=None,
                                          memory_footprint=None,
                                          priority=None,
                                          preemptive_execution=PreemptiveExecution.NON_PREEMPTIVE,
                                          deadline_criteria=Criticality.SOFT,
                                          energy_consumption=None)

sporadic_task_definition = SporadicTask(identifier=1,
                                        worst_case_execution_time=600,
                                        relative_deadline=1,
                                        best_case_execution_time=None,
                                        execution_time_distribution=None,
                                        memory_footprint=None,
                                        priority=None,
                                        preemptive_execution=PreemptiveExecution.NON_PREEMPTIVE,
                                        deadline_criteria=Criticality.SOFT,
                                        energy_consumption=None,
                                        minimum_interarrival_time=5)

job_specification = Job(identifier=0,
                        task=aperiodic_task_definition,
                        activation_time=1)

task_set = TaskSet(periodic_tasks=[periodic_task_definition],
                   aperiodic_tasks=[aperiodic_task_definition],
                   sporadic_tasks=[sporadic_task_definition])
```

## Processor specification

The processor specification (ProcessorDefinition) specify how is the platform where the tasks are running. Some
properties are only used when a thermal simulation is done.

The physical processor model is very simple, however the thermal model simulator can handle complex processor floor
plans (see the tertimuss.cubed_space_thermal_simulator package). 

It has the following properties:

- board_definition: Definition of the CPU board (only used in thermal simulation)
- cores_definition: List with the definition of each core. The key is the CPU id, and the value the definition
- measure_unit: The measuring unit in meters of the boards and core definition (only used in thermal simulation)

The definition of the cores (CoreDefinition) has the following properties:

- core_type: Type of the core
- location: Location of the board (only used in thermal simulation)

The definition of the board (BoardDefinition) has the following properties:

- dimensions: Dimensions of the board (only used in thermal simulation)
- material: Material of the board (only used in thermal simulation)
- location: Location of the board (only used in thermal simulation)

The definition of the core type (CoreTypeDefinition) has the following properties:  
- dimensions: Dimensions of the core type in units (only used in thermal simulation)
- material: Material of the core type (only used in thermal simulation)
- core_energy_consumption: Core energy consumption properties (only used in thermal simulation)
- available_frequencies: Cores available frequencies in Hz

The energy consumption properties have the following properties:  
- leakage_alpha: Leakage alpha (only used in thermal simulation)
- leakage_delta: Leakage delta (only used in thermal simulation)
- dynamic_alpha: Dynamic alpha (only used in thermal simulation)
- dynamic_beta: Dynamic beta (only used in thermal simulation)

Where dynamic power consumption = dynamic_alpha * F^3 + dynamic_beta and leakage power consumption = current temperature
* 2 * leakage_delta + leakage_alpha.

The total power consumption is the sum of dynamic power consumption and leakage power consumption.

### Example

```python
import math
from typing import Set, Dict
from tertimuss.simulation_lib.system_definition import ProcessorDefinition, CoreEnergyConsumption, CoreTypeDefinition, \
    BoardDefinition, CoreDefinition
from tertimuss.cubed_space_thermal_simulator.materials_pack import SiliconSolidMaterial, CooperSolidMaterial
from tertimuss.cubed_space_thermal_simulator import UnitDimensions, UnitLocation

number_of_cores: int = 4
available_frequencies: Set[int] = {500, 1000}
thermal_dissipation: float = 5

max_cpu_frequency: float = max(available_frequencies)
leakage_alpha: float = 0.001
leakage_delta: float = 0.1
dynamic_beta: float = 2
dynamic_alpha: float = (thermal_dissipation - dynamic_beta) * max_cpu_frequency ** -3

energy_consumption_properties = CoreEnergyConsumption(leakage_alpha=leakage_alpha, leakage_delta=leakage_delta,
                                                      dynamic_alpha=dynamic_alpha,
                                                      dynamic_beta=dynamic_beta)

core_type_definition = CoreTypeDefinition(dimensions=UnitDimensions(x=10, y=10, z=2),
                                          material=SiliconSolidMaterial(),
                                          core_energy_consumption=energy_consumption_properties,
                                          available_frequencies=available_frequencies)

number_of_columns = math.ceil(math.sqrt(number_of_cores))

lateral_size = number_of_columns * (3 + 10 + 3)

board_definition = BoardDefinition(dimensions=UnitDimensions(x=lateral_size, y=lateral_size, z=1),
                                   material=CooperSolidMaterial(),
                                   location=UnitLocation(x=0, y=0, z=0))

cores_definition: Dict[int, CoreDefinition] = {}

for i in range(number_of_cores):
    x_position = (3 + 10 + 3) * (i % number_of_columns) + 3
    y_position = (3 + 10 + 3) * (i // number_of_columns) + 3
    cores_definition[i] = CoreDefinition(core_type=core_type_definition,
                                         location=UnitLocation(x=x_position, y=y_position, z=2))

processor_definition = ProcessorDefinition(board_definition=board_definition,
                                           cores_definition=cores_definition,
                                           measure_unit=0.001)
```

## Environment specification

The environment specification (EnvironmentSpecification) specify how is the environment where the processor is
located. It is only used in thermal simulations.

Its definition has the following properties:  
- environment_properties: Properties of a fluid environment
- temperature: Temperature of the environment in Kelvin. It will remain constant among all the simulation

The fluid environment has the following property:  
- heat transfer coefficient: Convective Heat Transfer Coefficient (W / m^2 ºC)

### Example

```python
from tertimuss.cubed_space_thermal_simulator.materials_pack import AirForcedEnvironmentProperties
from tertimuss.simulation_lib.system_definition import EnvironmentSpecification

environment_specification = EnvironmentSpecification(environment_properties=AirForcedEnvironmentProperties(),
                                                     temperature=45 + 273.15)
```

