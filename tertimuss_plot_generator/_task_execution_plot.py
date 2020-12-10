from dataclasses import dataclass
from typing import Dict, Set, List

from matplotlib.figure import Figure

from tertimuss_simulation_lib.simulator import RawSimulationResult, JobSectionExecution
from tertimuss_simulation_lib.system_definition import TaskSet, Job, Task, PreemptiveExecution, Criticality


def generate_task_execution_plot(task_set: TaskSet, jobs: List[Job],
                                 schedule_result: RawSimulationResult) -> Figure:
    pass
