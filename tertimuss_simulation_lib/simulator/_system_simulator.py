import itertools
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Union, Set

from ._simulation_result import RawSimulationResult
from .._math_utils import list_lcm
from ..schedulers_definition import CentralizedAbstractScheduler
from ..system_definition import Job, TaskSet, HomogeneousCpuSpecification, EnvironmentSpecification


@dataclass
class SimulationOptionsSpecification:
    # True if is a debug simulation and debug messages should be showed
    id_debug: bool

    # True if want to simulate the thermal behaviour
    simulate_thermal_behaviour: bool


def _create_deadline_arrive_dict(lcm_frequency: int, jobs: List[Job]) -> Tuple[Dict[int, List[int]],
                                                                               Dict[int, List[int]]]:
    """
    Return a list ordered by arrive and by deadline of jobs containing the id of each job
    :param lcm_frequency:
    :param jobs:
    :return:
    """
    # Dict of activations
    activation_dict: Dict[int, List[int]] = {}
    for i in jobs:
        normalized_activation = round(i.activation_time * lcm_frequency)
        if activation_dict.__contains__(normalized_activation):
            activation_dict[normalized_activation].append(i.identification)
        else:
            activation_dict[normalized_activation] = [i.identification]

    # Dict of deadlines
    deadlines_dict: Dict[int, List[int]] = {}
    for i in jobs:
        normalized_absolute_deadline = round(i.absolute_deadline * lcm_frequency)
        if deadlines_dict.__contains__(normalized_absolute_deadline):
            deadlines_dict[normalized_absolute_deadline].append(i.identification)
        else:
            deadlines_dict[normalized_absolute_deadline] = [i.identification]

    return activation_dict, deadlines_dict


def execute_simulation(simulation_start_time: float,
                       simulation_end_time: float,
                       jobs: List[Job],
                       tasks: TaskSet,
                       cpu_specification: Union[HomogeneousCpuSpecification],
                       environment_specification: EnvironmentSpecification,
                       scheduler: CentralizedAbstractScheduler,
                       simulation_options: SimulationOptionsSpecification) -> Optional[RawSimulationResult]:
    # TODOLIST:
    # Simulation for homogeneous CPUs, Centralized Schedulers without thermal
    # Simulation for homogeneous CPUs, Centralized Schedulers with thermal
    # Add parameters check
    # Add simulation options control
    # Simulation for homogeneous CPUs, Distributed Schedulers with thermal

    # Check if scheduler is capable of execute task set
    can_schedule, error_message = scheduler.check_schedulability(cpu_specification, environment_specification, tasks)

    if not can_schedule:
        if error_message is not None:
            print("The scheduler can't schedule due to: ", error_message)
        else:
            print("The scheduler can't schedule")
        return None

    # Run scheduler offline phase
    cpu_frequency = scheduler.offline_stage(cpu_specification, environment_specification, tasks)

    # Create data structures for the simulation
    # Max frequency
    lcm_frequency = list_lcm(list(cpu_specification.cores_specification.available_frequencies))

    # Dict with activation and deadlines
    activation_dict, deadlines_dict = _create_deadline_arrive_dict(lcm_frequency, jobs)

    # Remaining jobs CC dict by id
    remaining_cc_dict: Dict[int, int] = {i.identification: i.execution_time for i in jobs}

    # Simulation step
    actual_lcm_cycle = simulation_start_time * lcm_frequency
    final_lcm_cycle = simulation_end_time * lcm_frequency

    # Major cycle
    major_cycle_lcm = list_lcm([round(i.relative_deadline * lcm_frequency) for i in tasks.periodic_tasks])

    # Jobs to task dict
    jobs_to_task_dict = {i.identification: i.task.identification for i in jobs}

    # Activate jobs set
    active_jobs = set()

    # Hard deadline task miss deadline
    hard_rt_task_miss_deadline = False

    # Jobs type dict
    hard_real_time_jobs: Set[int] = set()
    firm_real_time_jobs: Set[int] = set()
    soft_real_time_jobs: Set[int] = set()
    fully_preemptive_jobs: Set[int] = set()
    non_preemptive_jobs: Set[int] = set()

    # When is set the next scheduling point by quantum
    next_scheduling_point = None

    # Main control loop
    while actual_lcm_cycle < final_lcm_cycle and not hard_rt_task_miss_deadline:
        # Actual time in seconds
        actual_time_seconds = actual_lcm_cycle / lcm_frequency

        # Major cycle start event
        major_cycle_event_require_scheduling = scheduler.on_major_cycle_start(actual_time_seconds) \
            if actual_lcm_cycle % major_cycle_lcm == 0 else False

        # Job activation events
        activated_this_cycle = [(i, j) for i, j in activation_dict.items() if i <= actual_lcm_cycle]

        for i, j in activated_this_cycle:
            activation_dict.pop(i)
            for k in j:
                active_jobs.add(k)

        activation_event_require_scheduling_list = [
            scheduler.on_jobs_activation(actual_time_seconds, i / lcm_frequency, [(k, jobs_to_task_dict[k]) for k in j])
            for i, j in activated_this_cycle]

        activation_event_require_scheduling = any(activation_event_require_scheduling_list)

        # Job end event
        jobs_that_have_end = [i for i in active_jobs if remaining_cc_dict[i] == 0]

        for i in jobs_that_have_end:
            active_jobs.remove(i)

        end_event_require_scheduling = scheduler.on_job_execution_finished(actual_time_seconds, jobs_that_have_end)

        # Job missed deadline events
        deadline_this_cycle = [(i, j) for i, j in deadlines_dict.items() if i <= actual_lcm_cycle]

        for i, _ in deadline_this_cycle:
            deadlines_dict.pop(i)

        jobs_deadline_this_cycle: List[int] = list(itertools.chain(*[j for _, j in deadline_this_cycle]))

        deadline_missed_this_cycle = [i for i in jobs_deadline_this_cycle if i in active_jobs]

        for i in (j for j in deadline_missed_this_cycle if j in firm_real_time_jobs):
            active_jobs.remove(i)  # Remove firm real time from active set

        hard_rt_task_miss_deadline = any(
            (i in hard_real_time_jobs for i in deadline_this_cycle))  # If some jab is hard real time set the flag

        deadline_missed_event_require_scheduling = scheduler.on_jobs_deadline_missed(actual_time_seconds,
                                                                                     deadline_missed_this_cycle)

        # Do scheduling if required
        if not hard_rt_task_miss_deadline and (
                major_cycle_event_require_scheduling or
                activation_event_require_scheduling or
                end_event_require_scheduling or
                deadline_missed_event_require_scheduling or
                next_scheduling_point == actual_lcm_cycle):
            # TODO: Call scheduler
            # TODO: Update RawSimulationResult tables
            # TODO: If a non preemptive task have been preempted, its execution time must be restarted
            pass

        # TODO: Next cycle == min(keys(activation_dict), keys(deadline_dict), )

        # TODO: Once next loop is calculated update CC tables

        pass
