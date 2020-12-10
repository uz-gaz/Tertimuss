from dataclasses import dataclass
from typing import Dict, Set, List

import numpy
from matplotlib import pyplot
from matplotlib.figure import Figure

from tertimuss_simulation_lib.simulator import RawSimulationResult, JobSectionExecution
from tertimuss_simulation_lib.system_definition import TaskSet, Job, Task, PreemptiveExecution, Criticality


def generate_task_assignation_plot(task_set: TaskSet, jobs: List[Job],
                                   schedule_result: RawSimulationResult) -> Figure:
    fig1, ax1 = pyplot.subplots()
    x = numpy.linspace(0, 2 * numpy.pi, 400)
    y = numpy.sin(x ** 2)
    ax1.plot(x, y)
    ax1.set_title('Sharing Y axis')
    return fig1
