![Tertimuss logo](./docs/images/logo/logo_background.svg)

# Tertimuss: Simulation environment for Real-Time Multiprocessor Schedulers
![Python package](https://github.com/AbelChT/Tertimuss-Dev/workflows/Python%20package/badge.svg)

Tertimuss is a real-time scheduler evaluation tool. It allows the evaluation of the behavior of a scheduler with an easy interface to implement it. It is primarily designed for a first design phase of a scheduling algorithm where some computer architectural restrictions can be obviated.  
Using Tertimuss you can execute simulations using a proposed scheduler implementation (or one of the implemented schedulers) of multiprocessor with a customizable CPU definition as well as a customizable task set (it can be automatically generated too using common task generation algorithms). The simulation result can be numerical and graphical analyzed with some tools provided too.

## Installation
A Python 3.7 or greater version is required.

The recommended way to use Tertimuss is installing it in a Python virtual environment and using it as a library.

First, you will need a Python 3.7 or greater version installed on your computer.

To create a virtual environment (with name .venv) and activate it use the following commands:

```bash
$ python3 -m venv .venv --copies

# Execute the following line only if you are in a Unix like system (Linux/Mac/FreeBSD)
$ source .venv/bin/activate

# Execute the following line only if you are in a Windows system
$ .\.venv\Scripts\Activate.ps1
```

To install Tertimuss in the created virtual environment use the following command:

```bash
$ pip install .
```

## Usage

Once it is installed you can try your first simulation with Tertimuss:

```Python
# Import libraries
from tertimuss.schedulers.alecs import ALECSScheduler
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, \
    SimulationOptionsSpecification
from tertimuss.simulation_lib.system_definition import TaskSet, PeriodicTask, \
    PreemptiveExecution, Criticality
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, \
    default_environment_specification
from tertimuss.tasks_generator.deadline_generator import UniformIntegerDeadlineGenerator
from tertimuss.tasks_generator.periodic_tasks.implicit_deadlines import UUniFastDiscard
from tertimuss.visualization_generator import generate_task_execution_plot

# Simulation configuration
base_frequency = 1000
available_frequencies = {base_frequency}
number_of_cores = 4
number_of_tasks = 9

# Task generation
tasks_deadlines = UniformIntegerDeadlineGenerator.generate(number_of_tasks=number_of_tasks,
                                                            min_deadline=2,
                                                            max_deadline=12,
                                                            major_cycle=24)
x = UUniFastDiscard.generate(utilization=number_of_cores,
                                tasks_deadlines=tasks_deadlines,
                                processor_frequency=base_frequency)

# Definition of the task set
task_set = TaskSet(
    periodic_tasks=[
        PeriodicTask(identification=i,
                        worst_case_execution_time=j.worst_case_execution_time,
                        relative_deadline=j.deadline,
                        best_case_execution_time=None,
                        execution_time_distribution=None,
                        memory_footprint=None,
                        priority=None,
                        preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                        deadline_criteria=Criticality.HARD,
                        energy_consumption=None,
                        phase=None,
                        period=j.deadline) for i, j in enumerate(x)],
    aperiodic_tasks=[],
    sporadic_tasks=[]
)

# Execute simulation
simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
    tasks=task_set,
    aperiodic_tasks_jobs=[],
    sporadic_tasks_jobs=[],
    processor_definition=generate_default_cpu(number_of_cores, available_frequencies, 0, 0),
    environment_specification=default_environment_specification(),
    simulation_options=SimulationOptionsSpecification(id_debug=False),
    scheduler=ALECSScheduler(activate_debug=False)
)

# Display execution
fig = generate_task_execution_plot(task_set=task_set, schedule_result=simulation_result,
                                    title="Task execution",
                                    outline_boxes=True)

# Save execution in a file named "execution.svg"
fig.savefig("execution.svg")
```

This specification generate automatically 9 periodic tasks that will run over 4 cores using the scheduling algorithm ALECS and will save a diagram of the execution.

The diagram saved is the following:
![Execution example](./docs/images/readme/execution_example.svg)

Please, go to the tutorials page in the wiki to view more usage examples.

Also you can visit the reference page in the wiki to view the reference of all the functions and classes available. The same information can be accessed using the help command in a Python terminal (e.g. import tertimuss; help(tertimuss))

## Contributing
You can contribute either adding your own scheduler implementation, adding new features to the framework or proposing new features.

In case that you want to add a new scheduler implementation or a new feature, fork this repository and implement the new features in the development branch. Then send a pull request from your development branch to the development branch in this repository.

For more detailed explanation of the architecture of Tertimuss as well as some development guides, visit the development page in the wiki.

In case that you only want to propose a new feature or reporting a bug, use the issues section. 

## Citing
If you want to use tertimuss in your papers, you can cite it as:

```biblex
@misc{tertimuss,
  title = {{Tertimuss: Simulation environment for Real-Time Multiprocessor Schedulers}},
  year = {2019},
  note = {\url{https://webdiis.unizar.es/gaz/repositories/tertimuss}},
  urldate = {2021-01-27}
}
```

## License
The code in this repository, unless otherwise noted, is GNU GPLv3 licensed. See the `LICENSE` file in this repository.

