import itertools
from collections import deque
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

    arrive_deque = deque(sorted({i.arrive_cycle for i in jobs}))

    result_dict: Dict[int, Dict[int, int]] = {}

    next_event = arrive_deque.popleft()

    i = next_event

    number_of_cycles_in_major_cycle = round(major_cycle * processor_frequency)

    while i < number_of_cycles_in_major_cycle:
        executable_tasks = [j for j in jobs if j.deadline_cycle >= i >= j.arrive_cycle and j.pending_cycles > 0]
        if len(executable_tasks) == 0:
            actual_execution = -1

            # Calculate executed cycles in this iteration
            if len(arrive_deque) != 0:
                # move to the next job arrive
                next_i = arrive_deque.popleft()
            else:
                # end loop
                next_i = number_of_cycles_in_major_cycle

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

            # Calculate executed cycles in this iteration
            if len(arrive_deque) != 0:
                next_i = min(i + actual_execution_job.pending_cycles, arrive_deque[0])
                if next_i == arrive_deque[0]:
                    arrive_deque.popleft()

            else:
                next_i = i + actual_execution_job.pending_cycles

            actual_execution_job.pending_cycles -= next_i - i

        if actual_execution != last_execution:
            result_dict[i] = {0: actual_execution} if actual_execution != -1 else {}
            last_execution = actual_execution

        i = next_i

    return result_dict
