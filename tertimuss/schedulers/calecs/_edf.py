import itertools
from dataclasses import dataclass
from typing import List, Dict

import numpy

from tertimuss.simulation_lib.math_utils import list_float_lcm
from tertimuss.simulation_lib.system_definition import PeriodicTask


@dataclass
class _LocalJob:
    arrive_cycle: int
    pending_cycles: int
    associated_task: int
    deadline_cycle: int


def obtain_edf_cyclic_executive(processor_frequency: int, periodic_tasks: List[PeriodicTask]) \
        -> Dict[int, Dict[int, int]]:
    """
    Obtain EDF cyclic executive
    :param processor_frequency: frequency of the CPU
    :param periodic_tasks: set of periodic tasks
    :return: cyclic executive
    """
    major_cycle = list_float_lcm([i.relative_deadline for i in periodic_tasks])

    jobs: List[_LocalJob] = list(itertools.chain(*[[
        _LocalJob(arrive_cycle=round(j * i.relative_deadline * processor_frequency),
                  pending_cycles=i.worst_case_execution_time,
                  deadline_cycle=round((j + 1) * i.relative_deadline * processor_frequency),
                  associated_task=i.identification)
        for j in range(round(major_cycle / i.relative_deadline))] for i in periodic_tasks]))

    last_execution = -1

    result_dict: Dict[int, Dict[int, int]] = {}

    for i in range(round(major_cycle * processor_frequency)):
        executable_tasks = [j for j in jobs if j.deadline_cycle >= i >= j.arrive_cycle and j.pending_cycles > 0]
        if len(executable_tasks) == 0:
            actual_execution = -1
        else:
            # Obtain earliest deadline
            less_deadline = min(i.deadline_cycle for i in executable_tasks)
            less_deadline_tasks = [i for i in executable_tasks if less_deadline == i.deadline_cycle]

            # If actual executed task has the earliest deadline, select it
            if last_execution in (j.associated_task for j in less_deadline_tasks):
                actual_execution = last_execution
            else:
                # Find less remaining cycles to execute
                less_cycles_index = numpy.argmin(i.pending_cycles for i in less_deadline_tasks)
                actual_execution = less_deadline_tasks[less_cycles_index].associated_task

            actual_execution_job = next(j for j in executable_tasks if j.associated_task == actual_execution)
            actual_execution_job.pending_cycles -= 1

        if actual_execution != last_execution:
            result_dict[i] = {0: actual_execution} if actual_execution != -1 else {}
            last_execution = actual_execution

    return result_dict
