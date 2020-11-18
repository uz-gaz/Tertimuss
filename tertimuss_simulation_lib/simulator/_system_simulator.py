import itertools
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Union, Set

from cubed_space_thermal_simulator import TemperatureLocatedCube
from ._simulation_result import RawSimulationResult, JobSectionExecution, CPUUsedFrequency, \
    SimulationStackTraceHardRTDeadlineMissed
from .._math_utils import list_lcm
from ..schedulers_definition import CentralizedAbstractScheduler
from tertimuss_simulation_lib.system_definition import Job, TaskSet, HomogeneousCpuSpecification, \
    EnvironmentSpecification
from ..system_definition.utils import calculate_major_cycle


@dataclass
class SimulationOptionsSpecification:
    # True if is a debug simulation and debug messages should be showed
    id_debug: bool = False

    # True if want to simulate the thermal behaviour
    simulate_thermal_behaviour: bool = False

    # If false, the system won't check if the tasks returned by the scheduler is on the available task set.
    # It won't check if the returned frequency is correct.
    # If you are sure that your scheduler have a good behaviour turn it off can reduce the simulation time
    scheduler_selections_check: bool = True


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


def execute_simulation_major_cycle(tasks: TaskSet,
                                   aperiodic_tasks_jobs: List[Job],
                                   sporadic_tasks_jobs: List[Job],
                                   cpu_specification: Union[HomogeneousCpuSpecification],
                                   environment_specification: EnvironmentSpecification,
                                   scheduler: CentralizedAbstractScheduler,
                                   simulation_options: SimulationOptionsSpecification) -> Optional[RawSimulationResult]:
    major_cycle = calculate_major_cycle(tasks)

    number_of_periodic_ids = sum([round(major_cycle / i.relative_deadline) for i in tasks.periodic_tasks])
    number_of_ids = number_of_periodic_ids + len(aperiodic_tasks_jobs) + len(sporadic_tasks_jobs)

    job_ids_stack: deque = deque(
        Set.difference({i for i in range(number_of_ids)}, Set.union({i.identification for i in aperiodic_tasks_jobs},
                                                                    {i.identification for i in sporadic_tasks_jobs})))

    periodic_tasks_jobs: List[Job] = list(itertools.chain(*[[Job(job_ids_stack.pop(), i, j * i.relative_deadline)
                                                             for j in range(round(major_cycle / i.relative_deadline))]
                                                            for i in tasks.periodic_tasks]))

    return execute_simulation(0, major_cycle, periodic_tasks_jobs + aperiodic_tasks_jobs + sporadic_tasks_jobs, tasks,
                              cpu_specification, environment_specification, scheduler, simulation_options)


def execute_simulation(simulation_start_time: float,
                       simulation_end_time: float,
                       jobs: List[Job],
                       tasks: TaskSet,
                       cpu_specification: Union[HomogeneousCpuSpecification],
                       environment_specification: EnvironmentSpecification,
                       scheduler: CentralizedAbstractScheduler,
                       simulation_options: SimulationOptionsSpecification) -> Optional[RawSimulationResult]:
    # TODOLIST:
    # Simulation for homogeneous CPUs, Centralized Schedulers with thermal
    # Add parameters check
    #   Jobs ids
    #   Start and end of simulation
    #   CPU specification
    # Add simulation options control
    # Simulation for homogeneous CPUs, Distributed Schedulers with thermal
    # Add memory_footprint

    # Check if scheduler is capable of execute task set
    can_schedule, error_message = scheduler.check_schedulability(cpu_specification, environment_specification, tasks)

    if not can_schedule:
        if error_message is not None:
            print("The scheduler can't schedule due to: ", error_message)
        else:
            print("The scheduler can't schedule")
        return None

    # Number of cpus
    number_of_cpus = cpu_specification.cores_specification.number_of_cores

    # Run scheduler offline phase
    cpu_frequency = scheduler.offline_stage(cpu_specification, environment_specification, tasks)

    # Create data structures for the simulation
    # Max frequency
    lcm_frequency = list_lcm(list(cpu_specification.cores_specification.available_frequencies))

    # Dict with activation and deadlines
    activation_dict, deadlines_dict = _create_deadline_arrive_dict(lcm_frequency, jobs)

    # Jobs CC dict by id (this value is constant and only should be used for fast access to the original cc)
    jobs_cc_dict: Dict[int, int] = {i.identification: i.execution_time for i in jobs}

    # Remaining jobs CC dict by id
    remaining_cc_dict: Dict[int, int] = jobs_cc_dict.copy()

    # Simulation step
    actual_lcm_cycle = simulation_start_time * lcm_frequency
    final_lcm_cycle = round(simulation_end_time * lcm_frequency)

    # Major cycle
    major_cycle_lcm = list_lcm([round(i.relative_deadline * lcm_frequency) for i in tasks.periodic_tasks])

    # Jobs to task dict
    jobs_to_task_dict = {i.identification: i.task.identification for i in jobs}

    # Activate jobs set
    active_jobs = set()

    # Hard deadline task miss deadline
    hard_rt_task_miss_deadline = False

    # Only must take value if a hard real time is missed
    hard_real_time_deadline_missed_stack_trace: Optional[SimulationStackTraceHardRTDeadlineMissed] = None

    # Jobs type dict
    hard_real_time_jobs: Set[int] = set()
    firm_real_time_jobs: Set[int] = set()
    # soft_real_time_jobs: Set[int] = set()
    # fully_preemptive_jobs: Set[int] = set()
    non_preemptive_jobs: Set[int] = set()

    # When is set the next scheduling point by quantum
    next_scheduling_point = None

    # Jobs being executed
    jobs_being_executed_id: Dict[int, int] = {}

    #  Raw execution result tables
    job_sections_execution: Dict[int, List[JobSectionExecution]] = {i: [] for i in range(
        number_of_cpus)}  # List of jobs executed by each core
    cpus_frequencies: Dict[int, List[CPUUsedFrequency]] = {i: [] for i in range(
        number_of_cpus)}  # List of CPU frequencies used by each core
    scheduling_points: List[float] = []  # Points where the scheduler have made an scheduling
    temperature_measures: Dict[float, List[TemperatureLocatedCube]] = {}  # Measures of temperature

    # Jobs being executed extra information [CPU, [start time]]
    jobs_last_section_start_time: Dict[int, float] = {i.identification: -1 for i in jobs}
    jobs_last_cpu_used: Dict[int, int] = {i.identification: -1 for i in jobs}
    jobs_last_preemption_remaining_cycles: Dict[int, int] = {i.identification: -1 for i in jobs}

    # Last time frequency was set
    last_frequency_set_time = simulation_start_time

    # Main control loop
    while actual_lcm_cycle < final_lcm_cycle and not hard_rt_task_miss_deadline and \
            len(active_jobs) + len(activation_dict) > 0:
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

            # Update RawSimulationResult tables in case that a task end by cc
            # Remove it from executed tasks
            job_cpu_used = jobs_last_cpu_used[i]
            jobs_being_executed_id.pop(job_cpu_used)
            job_sections_execution[job_cpu_used].append(
                (JobSectionExecution(i, jobs_to_task_dict[i], jobs_last_section_start_time[i], actual_time_seconds,
                                     jobs_last_preemption_remaining_cycles[i] - remaining_cc_dict[i])))

        end_event_require_scheduling = scheduler.on_job_execution_finished(actual_time_seconds,
                                                                           jobs_that_have_end) if len(
            jobs_that_have_end) > 0 else False

        # Job missed deadline events
        deadline_this_cycle = [(i, j) for i, j in deadlines_dict.items() if i <= actual_lcm_cycle]

        for i, _ in deadline_this_cycle:
            deadlines_dict.pop(i)

        jobs_deadline_this_cycle: List[int] = list(itertools.chain(*[j for _, j in deadline_this_cycle]))

        deadline_missed_this_cycle = [i for i in jobs_deadline_this_cycle if i in active_jobs]

        for i in (j for j in deadline_missed_this_cycle if j in firm_real_time_jobs):
            active_jobs.remove(i)  # Remove firm real time from active set

            # Update RawSimulationResult tables in case that a task reach deadline and are firm
            job_cpu_used = jobs_last_cpu_used[i]

            if jobs_being_executed_id.__contains__(job_cpu_used) and jobs_being_executed_id[job_cpu_used] == i:
                jobs_being_executed_id.pop(job_cpu_used)
                job_sections_execution[job_cpu_used].append(
                    (JobSectionExecution(i, jobs_to_task_dict[i], jobs_last_section_start_time[i], actual_time_seconds,
                                         jobs_last_preemption_remaining_cycles[i] - remaining_cc_dict[i])))

        hard_rt_task_miss_deadline = any(
            (i in hard_real_time_jobs for i in jobs_deadline_this_cycle))  # If some jab is hard real time set the flag

        deadline_missed_event_require_scheduling = False

        if hard_rt_task_miss_deadline:
            hard_real_time_deadline_missed_stack_trace = SimulationStackTraceHardRTDeadlineMissed(actual_time_seconds, {
                j: remaining_cc_dict[j] for j in jobs_deadline_this_cycle if j in hard_real_time_jobs})
        else:
            # Check if a deadline missed require rescheduling
            deadline_missed_event_require_scheduling = scheduler.on_jobs_deadline_missed(actual_time_seconds,
                                                                                         deadline_missed_this_cycle) \
                if len(deadline_missed_this_cycle) > 0 else False

        # Do scheduling if required
        if not hard_rt_task_miss_deadline and (
                major_cycle_event_require_scheduling or
                activation_event_require_scheduling or
                end_event_require_scheduling or
                deadline_missed_event_require_scheduling or
                next_scheduling_point == actual_lcm_cycle) and len(active_jobs) > 0:
            # Call scheduler
            jobs_being_executed_id_next, cycles_until_next_scheduler_invocation, cores_frequency_next = \
                scheduler.schedule_policy(actual_time_seconds, active_jobs, jobs_being_executed_id, cpu_frequency, None)

            if cores_frequency_next is None:
                cores_frequency_next = cpu_frequency

            # Scheduler result checks
            if simulation_options.scheduler_selections_check:
                bad_scheduler_behaviour = not (cpu_specification.cores_specification.available_frequencies.__contains__(
                    cores_frequency_next) and all(
                    (0 <= i < number_of_cpus for i in jobs_being_executed_id_next.keys())) and all(
                    (i in active_jobs for i in jobs_being_executed_id_next.values())) and (
                                                       cycles_until_next_scheduler_invocation is None or
                                                       cycles_until_next_scheduler_invocation > 0))

                if bad_scheduler_behaviour:
                    exception_message = "Error due to bad scheduler behaviour\n" + \
                                        "\t Jobs to CPU assignation: " + str(jobs_being_executed_id_next) + "\n" + \
                                        "\t Active jobs: " + str(active_jobs) + "\n" + \
                                        "\t Selected frequency: " + str(cores_frequency_next) + "\n" + \
                                        "\t Available frequencies: " + \
                                        str(cpu_specification.cores_specification.available_frequencies)
                    raise Exception(exception_message)

            # Check if none preemptive task is preempted
            for i, j in jobs_being_executed_id.items():
                if j in non_preemptive_jobs and remaining_cc_dict[j] > 0 and (
                        not jobs_being_executed_id_next.__contains__(i) or jobs_being_executed_id_next[i] != j):
                    # If a non preemptive task have been preempted, its execution time must be restarted
                    remaining_cc_dict[j] = jobs_cc_dict[j]

            # Check if a task is preempted
            for i, j in jobs_being_executed_id.items():
                if not jobs_being_executed_id_next.__contains__(i) or jobs_being_executed_id_next[i] != j:
                    job_sections_execution[i].append(
                        (JobSectionExecution(j, jobs_to_task_dict[j], jobs_last_section_start_time[j],
                                             actual_time_seconds,
                                             jobs_last_preemption_remaining_cycles[j] - remaining_cc_dict[j])))

            # Check new tasks in execution
            for i, j in jobs_being_executed_id_next.items():
                if not jobs_being_executed_id.__contains__(i) or jobs_being_executed_id[i] != j:
                    jobs_last_preemption_remaining_cycles[j] = remaining_cc_dict[j]
                    jobs_last_section_start_time[j] = actual_time_seconds

            # Check if frequency have changed
            if cores_frequency_next != cpu_frequency:
                for i in range(number_of_cpus):
                    cpus_frequencies[i].append(
                        CPUUsedFrequency(cores_frequency_next, last_frequency_set_time, actual_time_seconds))

                last_frequency_set_time = actual_time_seconds

            # Update RawSimulationResult tables
            scheduling_points.append(actual_time_seconds)

            # Update frequency and executed tasks
            cpu_frequency = cores_frequency_next
            jobs_being_executed_id = jobs_being_executed_id_next
            next_scheduling_point = (cpu_frequency * cycles_until_next_scheduler_invocation + actual_lcm_cycle) \
                if cycles_until_next_scheduler_invocation is not None else None

            for i, j in jobs_being_executed_id.items():
                jobs_last_cpu_used[j] = i

        # In case that it has been missed the state of the variables must keep without alteration
        if not hard_rt_task_miss_deadline:
            # Next cycle == min(keys(activation_dict), keys(deadline_dict), remaining cycles)
            next_major_cycle = major_cycle_lcm * ((actual_lcm_cycle // major_cycle_lcm) + 1)

            next_job_end = min([remaining_cc_dict[i] for i in jobs_being_executed_id.values()]) * (
                    lcm_frequency // cpu_frequency) + actual_lcm_cycle if len(
                jobs_being_executed_id) > 0 else next_major_cycle

            next_job_deadline = min(deadlines_dict.keys()) if len(deadlines_dict) != 0 else next_major_cycle

            next_job_activation = min(activation_dict.keys()) if len(activation_dict) != 0 else next_major_cycle

            next_lcm_cycle = min([next_major_cycle, next_job_end, next_job_deadline, next_job_activation] + (
                [next_scheduling_point] if next_scheduling_point is not None else []))

            # This is just ceil((next_lcm_cycle - actual_lcm_cycle) / cpu_frequency) to advance an integer number
            # of cycles.
            # But with this formulation avoid floating point errors
            cc_to_advance = (((next_lcm_cycle - actual_lcm_cycle) // (lcm_frequency // cpu_frequency)) + (
                0 if (next_lcm_cycle - actual_lcm_cycle) % (lcm_frequency // cpu_frequency) == 0 else 1))

            # Calculated update CC tables
            for i in jobs_being_executed_id.values():
                remaining_cc_dict[i] -= cc_to_advance

            # Update actual_lcm_cycle
            actual_lcm_cycle += (lcm_frequency // cpu_frequency) * cc_to_advance

    # In the last cycle update RawSimulationResult tables (All jobs being executed)
    for i, j in jobs_being_executed_id.items():
        job_sections_execution[i].append(
            (JobSectionExecution(j, jobs_to_task_dict[j], jobs_last_section_start_time[j],
                                 actual_lcm_cycle / lcm_frequency,
                                 jobs_last_preemption_remaining_cycles[j] - remaining_cc_dict[j])))

    # In the last cycle update RawSimulationResult tables (Used frequencies)
    for i in range(number_of_cpus):
        cpus_frequencies[i].append(CPUUsedFrequency(cpu_frequency, last_frequency_set_time, simulation_end_time))

    return RawSimulationResult(job_sections_execution, cpus_frequencies, scheduling_points, temperature_measures,
                               hard_real_time_deadline_missed_stack_trace)
