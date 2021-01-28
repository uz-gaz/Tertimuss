import itertools
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set, Literal, Union

from tertimuss.cubed_space_thermal_simulator import TemperatureLocatedCube, LocatedCube, UnitLocation, UnitDimensions, \
    CubedSpace, CubedSpaceState, InternalTemperatureBoosterLocatedCube, ExternalTemperatureBoosterLocatedCube, \
    obtain_max_temperature
from tertimuss.cubed_space_thermal_simulator.physics_utils import create_energy_applicator

from ._simulation_result import RawSimulationResult, JobSectionExecution, CPUUsedFrequency, \
    SimulationStackTraceHardRTDeadlineMissed
from ..math_utils import list_int_lcm
from ..schedulers_definition import CentralizedAbstractScheduler
from ..system_definition import Job, TaskSet, EnvironmentSpecification, Criticality, PreemptiveExecution, \
    ProcessorDefinition
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

    # Thermal options specification
    thermal_simulation_type: Literal["DVFS", "TASK_CONSUMPTION_MEASURED"] = "DVFS"  # Control how the energy consumed
    # is expressed
    processor_mesh_division: int = 1  # Number of divisions done in each unit of the processor mesh during thermal
    # simulation
    thermal_simulation_precision: Literal["LOW", "MIDDLE", "HIGH"] = "HIGH"  # Precision in the thermal simulation
    # (method used to solve the model and float precision)

    # minimum number of thermal measures per second
    # TODO: Must be implemented in the simulation
    thermal_measure_rate: int = 1

    # Simulate memory occupation constraints
    simulate_memory_footprint: bool = False


def _create_deadline_arrive_dict(lcm_frequency: int, jobs: List[Job]) -> Tuple[Dict[int, List[int]],
                                                                               Dict[int, List[int]]]:
    """
    Return a list ordered by arrive and by deadline of jobs containing the id of each job
    :param lcm_frequency: Base frequency
    :param jobs: Jobs list
    :return:
        Dict[activation base cycle, job id]
        Dict[deadline base cycle, job id]
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


def execute_scheduler_simulation_simple(tasks: TaskSet,
                                        aperiodic_tasks_jobs: List[Job],
                                        sporadic_tasks_jobs: List[Job],
                                        processor_definition: ProcessorDefinition,
                                        environment_specification: EnvironmentSpecification,
                                        scheduler: Union[CentralizedAbstractScheduler],
                                        simulation_options: SimulationOptionsSpecification
                                        = SimulationOptionsSpecification()
                                        ) -> Tuple[RawSimulationResult, List[Job], float]:
    """
    Run a simulation without supplying the periodic jobs. It will be generated from the periodic tasks definition, and
     the simulation will be done between time 0 and the end of the first major cycle
    :param tasks: Group of tasks in the system. If None it will be the major cycle
    :param aperiodic_tasks_jobs: Aperiodic lobs in the system
    :param sporadic_tasks_jobs: Sporadic jobs in the system
    :param processor_definition: Definition of the CPU to use
    :param environment_specification: Specification of the environment
    :param scheduler: Centralized scheduler to use
    :param simulation_options: Options of the simulation
    :return:
     Simulation result
     Periodic jobs automatically generated
     Major cycle
    """

    major_cycle = calculate_major_cycle(tasks)

    number_of_periodic_ids = sum([round(major_cycle / i.period) for i in tasks.periodic_tasks])
    number_of_ids = number_of_periodic_ids + len(aperiodic_tasks_jobs) + len(sporadic_tasks_jobs)

    job_ids_stack: deque = deque(
        Set.difference({i for i in range(number_of_ids)}, Set.union({i.identification for i in aperiodic_tasks_jobs},
                                                                    {i.identification for i in sporadic_tasks_jobs})))

    periodic_tasks_jobs: List[Job] = list(itertools.chain(*[[Job(job_ids_stack.popleft(), i, j * i.period)
                                                             for j in range(round(major_cycle / i.period))]
                                                            for i in tasks.periodic_tasks]))

    return execute_scheduler_simulation(periodic_tasks_jobs + aperiodic_tasks_jobs + sporadic_tasks_jobs, tasks,
                                        processor_definition, environment_specification, scheduler,
                                        simulation_options), periodic_tasks_jobs, major_cycle


def execute_scheduler_simulation(jobs: List[Job],
                                 tasks: TaskSet,
                                 processor_definition: ProcessorDefinition,
                                 environment_specification: EnvironmentSpecification,
                                 scheduler: Union[CentralizedAbstractScheduler],
                                 simulation_options: SimulationOptionsSpecification
                                 = SimulationOptionsSpecification(),
                                 simulation_start_time: float = 0,
                                 simulation_end_time: Optional[float] = None) -> RawSimulationResult:
    """
    Run a simulation using a centralized scheduler
    :param jobs: Jobs in the system
    :param simulation_start_time: Time in seconds where the system start to make decisions. Time 0 is the start of the
     first major cycle
    :param simulation_end_time: Time in seconds since the start of the first major cycle where the simulation ends.
    :param tasks: Group of tasks in the system. If None it will be the major cycle
    :param processor_definition: Definition of the CPU to use
    :param environment_specification: Specification of the environment
    :param scheduler: Centralized scheduler to use
    :param simulation_options: Options of the simulation
    :return: Simulation result
    """
    # Check jobs
    if len(jobs) == 0:
        raise Exception("The system mist contains at least one job to simulate")

    jobs_ids = {i.identification for i in jobs}

    # Check tasks
    if len(jobs_ids) != len(jobs):
        raise Exception("Jobs must have different ids")

    tasks_ids = {i.identification for i in tasks.tasks()}

    # Check that all jobs have a valid task
    if any(i.task.identification not in tasks_ids for i in jobs):
        raise Exception("Some job have a non valid task associated")

    # Check tasks
    if len(jobs) == 0:
        raise Exception("The system mist contains at least one job to simulate")

    # Check tasks
    if len(tasks_ids) != len(tasks.tasks()):
        raise Exception("Tasks must have different ids")

    # Check start time
    if simulation_start_time < 0:
        raise Exception("Start time must be grater or equal than 0")

    # Check simulator end time
    if simulation_end_time is None:
        simulation_end_time = calculate_major_cycle(tasks)

    if simulation_start_time >= simulation_end_time:
        raise Exception("Start time must be lowest than end time")

    # Check scheduler
    if isinstance(scheduler, CentralizedAbstractScheduler):
        return _execute_centralized_scheduler_simulation(jobs, tasks, processor_definition, environment_specification,
                                                         scheduler, simulation_options, simulation_start_time,
                                                         simulation_end_time)
    else:
        raise Exception("The scheduler type provided is not supported")


def _generate_cubed_space(tasks: TaskSet,
                          processor_definition: ProcessorDefinition,
                          environment_specification: EnvironmentSpecification,
                          simulation_options: SimulationOptionsSpecification,
                          board_thermal_id: int) -> Tuple[CubedSpace, CubedSpaceState, Dict[Tuple[int, int], int],
                                                          Dict[Tuple[int, int], int]]:
    """
    Generate a cubed space thermal simulator from the system specification
    :param tasks: Group of tasks in the system
    :param processor_definition: Definition of the CPU to use
    :param environment_specification: Specification of the environment
    :param simulation_options: Options of the simulation
    :param board_thermal_id: Id of the cube that represents the board
    :return:
        Cubed space of the simulation
        Cubed space state of the simulation
        Dict [(core id, frequency in Hz)] -> External thermal source id that must be activated to simulate that a task
         is being executed in a CPU with a determinate frequency if DVSF is used
        Dict [(core id, task id)] -> External thermal source id that must be activated to simulate that a task is being
         executed in a CPU if energy based thermal model is used
    """
    cube_edge_size = processor_definition.measure_unit / simulation_options.processor_mesh_division

    scene_definition = {
        i: (j.core_type.material,
            LocatedCube(
                location=UnitLocation(x=j.location.x * simulation_options.processor_mesh_division,
                                      y=j.location.y * simulation_options.processor_mesh_division,
                                      z=j.location.z * simulation_options.processor_mesh_division),
                dimensions=UnitDimensions(x=j.core_type.dimensions.x * simulation_options.processor_mesh_division,
                                          y=j.core_type.dimensions.y * simulation_options.processor_mesh_division,
                                          z=j.core_type.dimensions.z * simulation_options.processor_mesh_division))
            ) for i, j in processor_definition.cores_definition.items()
    }
    # Board
    scene_definition[board_thermal_id] = (processor_definition.board_definition.material,
                                          LocatedCube(
                                              location=UnitLocation(
                                                  x=processor_definition.board_definition.location.x *
                                                    simulation_options.processor_mesh_division,
                                                  y=processor_definition.board_definition.location.y *
                                                    simulation_options.processor_mesh_division,
                                                  z=processor_definition.board_definition.location.z *
                                                    simulation_options.processor_mesh_division),
                                              dimensions=UnitDimensions(
                                                  x=processor_definition.board_definition.dimensions.x *
                                                    simulation_options.processor_mesh_division,
                                                  y=processor_definition.board_definition.dimensions.y *
                                                    simulation_options.processor_mesh_division,
                                                  z=processor_definition.board_definition.dimensions.z *
                                                    simulation_options.processor_mesh_division)))

    # Leakage power energy generators
    external_heat_generators_leakage_power = {
        i: create_energy_applicator((j.core_type.material,
                                     LocatedCube(
                                         location=UnitLocation(
                                             x=j.location.x * simulation_options.processor_mesh_division,
                                             y=j.location.y * simulation_options.processor_mesh_division,
                                             z=j.location.z * simulation_options.processor_mesh_division),
                                         dimensions=UnitDimensions(
                                             x=j.core_type.dimensions.x * simulation_options.processor_mesh_division,
                                             y=j.core_type.dimensions.y * simulation_options.processor_mesh_division,
                                             z=j.core_type.dimensions.z * simulation_options.processor_mesh_division))
                                     ),
                                    watts_to_apply=j.core_type.core_energy_consumption.leakage_alpha,
                                    cube_edge_size=cube_edge_size
                                    ) for i, j in processor_definition.cores_definition.items()
    }

    internal_heat_generators_leakage_power = {
        i: InternalTemperatureBoosterLocatedCube(
            location=UnitLocation(
                x=j.location.x * simulation_options.processor_mesh_division,
                y=j.location.y * simulation_options.processor_mesh_division,
                z=j.location.z * simulation_options.processor_mesh_division),
            dimensions=UnitDimensions(
                x=j.core_type.dimensions.x * simulation_options.processor_mesh_division,
                y=j.core_type.dimensions.y * simulation_options.processor_mesh_division,
                z=j.core_type.dimensions.z * simulation_options.processor_mesh_division),
            boostRateMultiplier=j.core_type.core_energy_consumption.leakage_delta
        ) for i, j in processor_definition.cores_definition.items()
    }

    # Dynamic energy external heat generators
    core_frequency_energy_activator_id: Dict[Tuple[int, int], int] = {}
    core_task_energy_activator_id: Dict[Tuple[int, int], int] = {}

    if simulation_options.thermal_simulation_type == "DVFS":
        external_heat_generators_dynamic_energy: Dict[int, ExternalTemperatureBoosterLocatedCube] = {}
        for i, j in processor_definition.cores_definition.items():
            for f in j.core_type.available_frequencies:
                generator_id = len(external_heat_generators_dynamic_energy) + \
                               len(external_heat_generators_leakage_power)
                core_frequency_energy_activator_id[(i, f)] = generator_id
                external_heat_generators_dynamic_energy[generator_id] = create_energy_applicator(
                    (j.core_type.material,
                     LocatedCube(
                         location=UnitLocation(
                             x=j.location.x * simulation_options.processor_mesh_division,
                             y=j.location.y * simulation_options.processor_mesh_division,
                             z=j.location.z * simulation_options.processor_mesh_division),
                         dimensions=UnitDimensions(
                             x=j.core_type.dimensions.x * simulation_options.processor_mesh_division,
                             y=j.core_type.dimensions.y * simulation_options.processor_mesh_division,
                             z=j.core_type.dimensions.z * simulation_options.processor_mesh_division))
                     ),
                    watts_to_apply=j.core_type.core_energy_consumption.dynamic_alpha * (f ** 3) +
                                   j.core_type.core_energy_consumption.dynamic_beta,
                    cube_edge_size=cube_edge_size
                )
    elif simulation_options.thermal_simulation_type == "TASK_CONSUMPTION_MEASURED":
        external_heat_generators_dynamic_energy: Dict[int, ExternalTemperatureBoosterLocatedCube] = {}
        for i, j in processor_definition.cores_definition.items():
            for k in tasks.tasks():
                generator_id = len(external_heat_generators_dynamic_energy) + \
                               len(external_heat_generators_leakage_power)
                core_task_energy_activator_id[(i, k.identification)] = generator_id
                external_heat_generators_dynamic_energy[generator_id] = create_energy_applicator(
                    (j.core_type.material,
                     LocatedCube(
                         location=UnitLocation(
                             x=j.location.x * simulation_options.processor_mesh_division,
                             y=j.location.y * simulation_options.processor_mesh_division,
                             z=j.location.z * simulation_options.processor_mesh_division),
                         dimensions=UnitDimensions(
                             x=j.core_type.dimensions.x * simulation_options.processor_mesh_division,
                             y=j.core_type.dimensions.y * simulation_options.processor_mesh_division,
                             z=j.core_type.dimensions.z * simulation_options.processor_mesh_division))
                     ),
                    watts_to_apply=k.energy_consumption,
                    cube_edge_size=cube_edge_size
                )
    else:
        external_heat_generators_dynamic_energy: Dict[int, ExternalTemperatureBoosterLocatedCube] = {}

    cubed_space = CubedSpace(
        material_cubes=scene_definition,
        cube_edge_size=cube_edge_size,
        external_temperature_booster_points={**external_heat_generators_leakage_power,
                                             **external_heat_generators_dynamic_energy},
        internal_temperature_booster_points=internal_heat_generators_leakage_power,
        environment_properties=environment_specification.environment_properties,
        simulation_precision=simulation_options.thermal_simulation_precision)

    initial_state = cubed_space.create_initial_state(
        default_temperature=environment_specification.temperature,
        environment_temperature=environment_specification.temperature
    )

    return cubed_space, initial_state, core_frequency_energy_activator_id, core_task_energy_activator_id


def _execute_centralized_scheduler_simulation(jobs: List[Job],
                                              tasks: TaskSet,
                                              processor_definition: ProcessorDefinition,
                                              environment_specification: EnvironmentSpecification,
                                              scheduler: CentralizedAbstractScheduler,
                                              simulation_options: SimulationOptionsSpecification,
                                              simulation_start_time: float,
                                              simulation_end_time: float) -> RawSimulationResult:
    """
    Run a simulation using a centralized scheduler
    :param jobs: Jobs in the system
    :param simulation_start_time: Time in seconds where the system start to make decisions. Time 0 is the start of the
     first major cycle
    :param simulation_end_time: Time in seconds since the start of the first major cycle where the simulation ends.
    :param tasks: Group of tasks in the system
    :param processor_definition: Definition of the CPU to use
    :param environment_specification: Specification of the environment
    :param scheduler: Centralized scheduler to use
    :param simulation_options: Options of the simulation
    :return: Simulation result
    """
    # Possible frequencies
    # As we are simulating with a centralized scheduler, only frequencies possibles in all cores are available
    available_frequencies = Set.intersection(
        *[i.core_type.available_frequencies for i in processor_definition.cores_definition.values()])

    if len(available_frequencies) == 0:
        return RawSimulationResult(have_been_scheduled=False,
                                   scheduler_acceptance_error_message="at least one frequency must be shared by all" +
                                                                      " cores in a centralized scheduler simulation",
                                   job_sections_execution={}, cpus_frequencies={},
                                   scheduling_points=[], temperature_measures={},
                                   hard_real_time_deadline_missed_stack_trace=None,
                                   memory_usage_record=None)

    # Unit mesh division
    if simulation_options.processor_mesh_division < 1:
        return RawSimulationResult(have_been_scheduled=False,
                                   scheduler_acceptance_error_message="mesh division must be greater than 0",
                                   job_sections_execution={}, cpus_frequencies={},
                                   scheduling_points=[], temperature_measures={},
                                   hard_real_time_deadline_missed_stack_trace=None,
                                   memory_usage_record=None)

    # Number of cpus
    number_of_cpus = len(processor_definition.cores_definition)

    # Check if CPU ids go from 0 to number_of_tasks - 1
    cpus_ids_corrects: bool = all(0 <= i < number_of_cpus for i in processor_definition.cores_definition.keys())

    if not cpus_ids_corrects:
        return RawSimulationResult(have_been_scheduled=False,
                                   scheduler_acceptance_error_message="Processors id must go from 0 to the number of" +
                                                                      " CPUS - 1",
                                   job_sections_execution={}, cpus_frequencies={},
                                   scheduling_points=[], temperature_measures={},
                                   hard_real_time_deadline_missed_stack_trace=None,
                                   memory_usage_record=None)

    # Check if scheduler is capable of execute task set
    can_schedule, error_message = scheduler.check_schedulability(processor_definition, environment_specification, tasks)

    if not can_schedule:
        return RawSimulationResult(have_been_scheduled=False,
                                   scheduler_acceptance_error_message="the scheduler can't schedule"
                                   if error_message is None else error_message,
                                   job_sections_execution={}, cpus_frequencies={},
                                   scheduling_points=[], temperature_measures={},
                                   hard_real_time_deadline_missed_stack_trace=None,
                                   memory_usage_record=None)

    # Run scheduler offline phase
    cpu_frequency = scheduler.offline_stage(processor_definition, environment_specification, tasks)

    # Create data structures for the simulation
    # Max frequency
    lcm_frequency = list_int_lcm(list(available_frequencies))

    # Dict with activation and deadlines
    activation_dict, deadlines_dict = _create_deadline_arrive_dict(lcm_frequency, jobs)

    # Jobs CC dict by id (this value is constant and only should be used for fast access to the original cc)
    jobs_cc_dict: Dict[int, int] = {i.identification: i.execution_time for i in jobs}

    # Remaining jobs CC dict by id
    remaining_cc_dict: Dict[int, int] = jobs_cc_dict.copy()

    # Simulation step
    actual_lcm_cycle: int = round(simulation_start_time * lcm_frequency)
    final_lcm_cycle: int = round(simulation_end_time * lcm_frequency)

    # Major cycle
    major_cycle_lcm = list_int_lcm([round(i.period * lcm_frequency) for i in tasks.periodic_tasks])

    # Jobs to task dict
    jobs_to_task_dict = {i.identification: i.task.identification for i in jobs}

    # Activate jobs set
    active_jobs = set()

    # Hard deadline task miss deadline
    hard_rt_task_miss_deadline = False

    # Only must take value if a hard real time is missed
    hard_real_time_deadline_missed_stack_trace: Optional[SimulationStackTraceHardRTDeadlineMissed] = None

    # Jobs type dict
    hard_real_time_jobs: Set[int] = {i.identification for i in jobs if i.task.deadline_criteria == Criticality.HARD}
    firm_real_time_jobs: Set[int] = {i.identification for i in jobs if i.task.deadline_criteria == Criticality.FIRM}
    non_preemptive_jobs: Set[int] = {i.identification for i in jobs if
                                     i.task.preemptive_execution == PreemptiveExecution.NON_PREEMPTIVE}

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
    temperature_measures: Dict[float, Dict[int, TemperatureLocatedCube]] = {}  # Measures of temperature

    # Jobs being executed extra information [CPU, [start time]]
    jobs_last_section_start_time: Dict[int, float] = {i.identification: -1 for i in jobs}
    jobs_last_cpu_used: Dict[int, int] = {i.identification: -1 for i in jobs}
    jobs_last_preemption_remaining_cycles: Dict[int, int] = {i.identification: -1 for i in jobs}

    # Last time frequency was set
    last_frequency_set_time = simulation_start_time

    # Board id
    board_thermal_id: int = number_of_cpus

    # Available memory
    jobs_memory_consumption: Dict[int, int] = {
        i.identification: i.task.memory_footprint if i.task.memory_footprint is not None else 0 for i in jobs
    }
    memory_usage: int = 0
    memory_usage_record: Dict[float, int] = {}

    # Energy management objects
    cubed_space: Optional[CubedSpace] = None
    initial_state: Optional[CubedSpaceState] = None
    core_frequency_energy_activator: Optional[Dict[Tuple[int, int], int]] = None
    core_task_energy_activator: Optional[Dict[Tuple[int, int], int]] = None

    # Thermal options
    if simulation_options.simulate_thermal_behaviour:
        cubed_space, initial_state, core_frequency_energy_activator, core_task_energy_activator = _generate_cubed_space(
            tasks, processor_definition, environment_specification,
            simulation_options, board_thermal_id)

    # Main control loop
    while actual_lcm_cycle < final_lcm_cycle and not hard_rt_task_miss_deadline and \
            len(active_jobs) + len(activation_dict) > 0:
        # Actual time in seconds
        actual_time_seconds = actual_lcm_cycle / lcm_frequency

        # Record temperature
        if simulation_options.simulate_thermal_behaviour:
            cubes_temperatures = cubed_space.obtain_temperature(initial_state)
            temperature_measures[actual_time_seconds] = cubes_temperatures
            cores_max_temperature = obtain_max_temperature(cubes_temperatures)
            cores_max_temperature.pop(board_thermal_id)

        # Record memory usage
        if simulation_options.simulate_memory_footprint:
            memory_usage_record[actual_time_seconds] = memory_usage

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

            # Remove job from memory
            if simulation_options.simulate_memory_footprint:
                memory_usage = memory_usage - jobs_memory_consumption[i]

        end_event_require_scheduling = scheduler.on_job_execution_finished(actual_time_seconds, jobs_that_have_end) \
            if len(jobs_that_have_end) > 0 else False

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

                # Remove job from memory
                if simulation_options.simulate_memory_footprint:
                    memory_usage = memory_usage - jobs_memory_consumption[i]

        hard_rt_task_miss_deadline = any(
            (i in hard_real_time_jobs for i in
             deadline_missed_this_cycle))  # If some jab is hard real time set the flag

        deadline_missed_event_require_scheduling = False

        if hard_rt_task_miss_deadline:
            hard_real_time_deadline_missed_stack_trace = SimulationStackTraceHardRTDeadlineMissed(actual_time_seconds, {
                j: remaining_cc_dict[j] for j in deadline_missed_this_cycle if j in hard_real_time_jobs})
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
                bad_scheduler_behaviour = not (available_frequencies.__contains__(cores_frequency_next) and all(
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
                                        str(available_frequencies) + "\n" + \
                                        "\t Actual time: " + str(actual_time_seconds)
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

            # Update memory usage
            if simulation_options.simulate_memory_footprint:
                memory_usage = memory_usage - sum(jobs_memory_consumption[i] for i in jobs_being_executed_id.values()) \
                               + sum(jobs_memory_consumption[i] for i in jobs_being_executed_id_next.values())

            # Update RawSimulationResult tables
            scheduling_points.append(actual_time_seconds)

            # Update frequency and executed tasks
            cpu_frequency = cores_frequency_next
            jobs_being_executed_id = jobs_being_executed_id_next
            next_scheduling_point = ((lcm_frequency // cpu_frequency) * cycles_until_next_scheduler_invocation +
                                     actual_lcm_cycle) if cycles_until_next_scheduler_invocation is not None else None

            for i, j in jobs_being_executed_id.items():
                jobs_last_cpu_used[j] = i

        # In case that it has been missed the state of the variables must keep without alteration
        if not hard_rt_task_miss_deadline:
            # Next cycle == min(keys(activation_dict), keys(deadline_dict), remaining cycles)
            next_major_cycle: int = major_cycle_lcm * ((actual_lcm_cycle // major_cycle_lcm) + 1)

            next_job_end: int = min([remaining_cc_dict[i] for i in jobs_being_executed_id.values()]) * (
                    lcm_frequency // cpu_frequency) + actual_lcm_cycle if len(
                jobs_being_executed_id) > 0 else next_major_cycle

            next_job_deadline: int = min(deadlines_dict.keys()) if len(deadlines_dict) != 0 else next_major_cycle

            next_job_activation: int = min(activation_dict.keys()) if len(activation_dict) != 0 else next_major_cycle

            next_lcm_cycle: int = min([next_major_cycle, next_job_end, next_job_deadline, next_job_activation] + (
                [next_scheduling_point] if next_scheduling_point is not None else []))

            # This is just ceil((next_lcm_cycle - actual_lcm_cycle) / cpu_frequency) to advance an integer number
            # of cycles.
            # But with this formulation avoid floating point errors
            cc_to_advance = (((next_lcm_cycle - actual_lcm_cycle) // (lcm_frequency // cpu_frequency)) + (
                0 if (next_lcm_cycle - actual_lcm_cycle) % (lcm_frequency // cpu_frequency) == 0 else 1))

            # Calculated update CC tables
            for i in jobs_being_executed_id.values():
                remaining_cc_dict[i] -= cc_to_advance

            # Obtain temperature in the next simulation point
            if simulation_options.simulate_thermal_behaviour:
                if simulation_options.thermal_simulation_type == "DVFS":
                    external_energy_point_execution = {core_frequency_energy_activator[(used_cpu, cpu_frequency)] for
                                                       used_cpu in jobs_being_executed_id.keys()}

                elif simulation_options.thermal_simulation_type == "TASK_CONSUMPTION_MEASURED":
                    external_energy_point_execution = {core_task_energy_activator[(used_cpu, task_executed)] for
                                                       used_cpu, task_executed in jobs_being_executed_id.keys()}
                else:
                    external_energy_point_execution = set()

                # Apply energy
                initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                         amount_of_time=cc_to_advance / cpu_frequency,
                                                         external_energy_application_points=Set.union(
                                                             external_energy_point_execution,
                                                             {i for i in range(number_of_cpus)}),
                                                         internal_energy_application_points={i for i in
                                                                                             range(number_of_cpus)})

            # Update actual_lcm_cycle
            actual_lcm_cycle += (lcm_frequency // cpu_frequency) * cc_to_advance

    # In the last cycle update RawSimulationResult tables (All jobs being executed)
    for i, j in jobs_being_executed_id.items():
        job_sections_execution[i].append(
            (JobSectionExecution(j, jobs_to_task_dict[j], jobs_last_section_start_time[j],
                                 actual_lcm_cycle / lcm_frequency,
                                 jobs_last_preemption_remaining_cycles[j] - remaining_cc_dict[j])))

    # Record temperature
    if simulation_options.simulate_thermal_behaviour:
        cubes_temperatures = cubed_space.obtain_temperature(initial_state)
        temperature_measures[actual_lcm_cycle / lcm_frequency] = cubes_temperatures

    # In the last cycle update RawSimulationResult tables (Used frequencies)
    for i in range(number_of_cpus):
        cpus_frequencies[i].append(CPUUsedFrequency(cpu_frequency, last_frequency_set_time, simulation_end_time))

    return RawSimulationResult(have_been_scheduled=True, scheduler_acceptance_error_message=None,
                               job_sections_execution=job_sections_execution, cpus_frequencies=cpus_frequencies,
                               scheduling_points=scheduling_points, temperature_measures=temperature_measures,
                               hard_real_time_deadline_missed_stack_trace=hard_real_time_deadline_missed_stack_trace,
                               memory_usage_record=memory_usage_record if simulation_options.simulate_memory_footprint
                               else None)
