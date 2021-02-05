from typing import Set, Dict, Optional, Tuple, List

from ._bpp_based_algorithms import BestFitDescendantBPPBasedPartitionAlgorithm
from ._edf import obtain_edf_cyclic_executive
from ._task import ImplicitDeadlineTask
from tertimuss.simulation_lib.math_utils import list_int_lcm
from tertimuss.simulation_lib.schedulers_definition import CentralizedAbstractScheduler
from tertimuss.simulation_lib.system_definition import ProcessorDefinition, EnvironmentSpecification, TaskSet, \
    CoreDefinition, CoreTypeDefinition, PreemptiveExecution
from ..alecs import ALECSScheduler
from ...simulation_lib.system_definition.utils import calculate_major_cycle


class CALECSScheduler(CentralizedAbstractScheduler):
    """
       Implements the Clustered Allocation and Execution Control Scheduler (CALECS)

       The actual implementation only allows periodic tasks (the original specification allows aperiodic too)

       References:
           The article has been sent for revision
       """
    def __init__(self, activate_debug: bool, store_clusters_obtained: bool):
        """
        Create the CALECS scheduler instance

        :param activate_debug: True if want to communicate the scheduler to be in debug mode
        :param store_clusters_obtained: True if want to access later to the clusters obtained by the scheduler
        """
        super().__init__(activate_debug)

        # Declare class variables
        self.__scheduling_points: Dict[int, Dict[int, int]] = {}
        self.__major_cycle: float = 0
        self.__task_to_job: Dict[int, int] = {}

        # Store the number of CPUs in each cluster
        self.__clusters_obtained: Optional[List[int]] = [] if store_clusters_obtained else None

    def get_clusters_obtained(self) -> Optional[List[int]]:
        """
        Return the configuration of the clusters obtained

        :return: number of cpus in each cluster
        """
        return self.__clusters_obtained

    def check_schedulability(self, processor_definition: ProcessorDefinition,
                             environment_specification: EnvironmentSpecification, task_set: TaskSet) -> [bool,
                                                                                                         Optional[str]]:
        """
        Return true if the scheduler can be able to schedule the system. In negative case, it can return a reason.
        In example, an scheduler that only can work with periodic tasks with phase=0, can return
         [false, "Only can schedule tasks with phase=0"]

        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        only_0_phase = all(i.phase is None or i.phase == 0 for i in task_set.periodic_tasks)

        only_periodic_tasks = len(task_set.sporadic_tasks) + len(task_set.aperiodic_tasks) == 0

        only_implicit_deadline = all(i.relative_deadline == i.period for i in task_set.periodic_tasks)

        only_fully_preemptive = all(i.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE
                                    for i in task_set.periodic_tasks)

        if not (only_0_phase and only_periodic_tasks and only_implicit_deadline and only_fully_preemptive):
            return False, "Error: Only implicit deadline, fully preemptive, 0 phase periodic tasks are allowed"

        m = len(processor_definition.cores_definition)

        clock_available_frequencies = list(Set.intersection(*[i.core_type.available_frequencies for i
                                                              in processor_definition.cores_definition.values()]))

        # Calculate F start
        major_cycle = calculate_major_cycle(task_set)

        available_frequencies = [actual_frequency for actual_frequency in clock_available_frequencies
                                 if sum([i.worst_case_execution_time * round(major_cycle / i.period)
                                         for i in task_set.periodic_tasks]) <= m * round(major_cycle * actual_frequency)
                                 and all([i.worst_case_execution_time * round(major_cycle / i.period)
                                          <= round(major_cycle * actual_frequency) for i in task_set.periodic_tasks])]

        if len(available_frequencies) == 0:
            return False, "Error: Schedule is not feasible"

        # All tests passed
        return True, None

    def offline_stage(self, processor_definition: ProcessorDefinition,
                      environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
        """
        Method to implement with the offline stage scheduler tasks

        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        m = len(processor_definition.cores_definition)

        clock_available_frequencies = Set.intersection(*[i.core_type.available_frequencies for i
                                                         in processor_definition.cores_definition.values()])

        # Calculate F start
        major_cycle = calculate_major_cycle(task_set)
        self.__major_cycle = major_cycle

        available_frequencies = (actual_frequency for actual_frequency in clock_available_frequencies
                                 if sum([i.worst_case_execution_time * round(major_cycle / i.period)
                                         for i in task_set.periodic_tasks]) <= m * round(major_cycle * actual_frequency)
                                 and all([i.worst_case_execution_time * round(major_cycle / i.period)
                                          <= round(major_cycle * actual_frequency) for i in task_set.periodic_tasks]))

        # F star in HZ
        f_star_hz = min(available_frequencies)

        periodic_tasks_dict = {i.identification: i for i in task_set.periodic_tasks}

        task_set_calecs: Dict[int, ImplicitDeadlineTask] = {
            i.identification: ImplicitDeadlineTask(i.worst_case_execution_time, round(i.period * f_star_hz))
            for i in task_set.periodic_tasks}

        major_cycle_cycles: int = list_int_lcm([i.d for i in task_set_calecs.values()])

        used_cycles = sum([i.c * (major_cycle_cycles // i.d) for i in task_set_calecs.values()])

        number_of_used_processors = next(i for i in range(1, m + 1) if major_cycle_cycles * i >= used_cycles)

        free_cycles = major_cycle_cycles * number_of_used_processors - used_cycles

        if free_cycles != 0:
            task_set_calecs[-1] = ImplicitDeadlineTask(free_cycles, major_cycle_cycles)

        partition_algorithm = BestFitDescendantBPPBasedPartitionAlgorithm()

        partitions_obtained: List[Tuple[int, Set[int]]] = partition_algorithm.do_partition(task_set_calecs,
                                                                                           number_of_used_processors)

        # Save the clusters obtained
        if self.__clusters_obtained is not None:
            self.__clusters_obtained = [i for i, _ in partitions_obtained]

        last_cpu_id_used = 0

        clusters_scheduling_points = []

        # Partitions done
        for utilization, task_set_loop in partitions_obtained:
            local_major_cycle = list_int_lcm(
                [round(periodic_tasks_dict[i].relative_deadline * f_star_hz) for i in task_set_loop if i != -1])
            number_of_major_cycles = major_cycle_cycles // local_major_cycle

            # Cores used
            local_used_cores_ids: List[int] = list(range(last_cpu_id_used, last_cpu_id_used + utilization))

            if utilization == 1:
                scheduling_points = obtain_edf_cyclic_executive(
                    periodic_tasks=[periodic_tasks_dict[i] for i in task_set_loop if i != -1],
                    processor_frequency=f_star_hz)
            else:
                local_used_cores = [
                    (i, CoreDefinition(location=processor_definition.cores_definition[j].location,
                                       core_type=CoreTypeDefinition(
                                           dimensions=processor_definition.cores_definition[j].core_type.dimensions,
                                           material=processor_definition.cores_definition[j].core_type.material,
                                           core_energy_consumption=
                                           processor_definition.cores_definition[j].core_type.core_energy_consumption,
                                           available_frequencies={f_star_hz})))
                    # preemption_cost=
                    # processor_definition.cores_definition[j].core_type.preemption_cost)))
                    for i, j in enumerate(local_used_cores_ids)]

                # migration_costs = {
                #     (i, j): processor_definition.migration_costs[(local_used_cores_ids[i], local_used_cores_ids[j])]
                #     for i in range(utilization) for j in range(utilization) if i != j}

                local_processor_definition = ProcessorDefinition(board_definition=processor_definition.board_definition,
                                                                 cores_definition={k: j for k, (i, j) in
                                                                                   enumerate(local_used_cores)},
                                                                 measure_unit=processor_definition.measure_unit)
                # migration_costs=migration_costs)

                local_task_set = TaskSet(periodic_tasks=[periodic_tasks_dict[i] for i in task_set_loop if i != -1],
                                         aperiodic_tasks=[],
                                         sporadic_tasks=[])

                local_scheduler = ALECSScheduler(self.is_debug)
                local_scheduler.offline_stage(processor_definition=local_processor_definition,
                                              task_set=local_task_set,
                                              environment_specification=environment_specification)
                scheduling_points = local_scheduler.get_scheduling_points()

            # Update last used CPU
            last_cpu_id_used += utilization

            # Replicate scheduling points number_of_major_cycles times
            # Translate scheduling points to real CPUs IDs
            cluster_execution_interval = {
                i + (local_major_cycle * k): {local_used_cores_ids[r]: q for r, q in j.items()}
                for i, j in scheduling_points.items()
                for k in range(number_of_major_cycles)}

            # Append data to global scheduling_points
            clusters_scheduling_points.append(cluster_execution_interval)

        # Obtain all scheduling points
        scheduling_points_global = Set.union(*[set(i.keys()) for i in clusters_scheduling_points])

        last_scheduling_point = [{} for _ in range(len(clusters_scheduling_points))]

        for i in sorted(scheduling_points_global):
            # Update last scheduling points
            for j, k in enumerate(clusters_scheduling_points):
                if k.__contains__(i):
                    last_scheduling_point[j] = k[i]

            # Update actual scheduling point
            actual_scheduling_point = {}
            for j in last_scheduling_point:
                actual_scheduling_point.update(j)

            self.__scheduling_points[i] = actual_scheduling_point

        return f_star_hz

    def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                        jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                        cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police

        :param global_time: Time in seconds since the simulation starts
        :param jobs_being_executed_id: Ids of the jobs that are currently executed on the system. The dictionary has as
         key the CPU id (it goes from 0 to number of CPUs - 1), and as value the job id.
        :param active_jobs_id: Identifications of the jobs that are currently active
         (look in :ref:..system_definition.DeadlineCriteria for more info) and can be executed.
        :param cores_frequency: Frequencies of cores on the scheduler invocation in Hz.
        :param cores_max_temperature: Max temperature of each core. The dictionary has as
         key the CPU id, and as value the temperature in Kelvin degrees.
        :return: Tuple of [
         Jobs CPU assignation. The dictionary has as key the CPU id, and as value the job id,
         Cycles to execute until the next invocation of the scheduler. If None, it won't be executed until a system
         event trigger its invocation,
         CPU frequency. If None, it will maintain the last used frequency (cores_frequency)
        ]
        """
        actual_execution_cycle = round(global_time * cores_frequency) % round(self.__major_cycle * cores_frequency)

        next_scheduling_point = next(i for i in sorted(self.__scheduling_points.keys()) +
                                     [round(self.__major_cycle * cores_frequency)] if i > actual_execution_cycle)

        return ({k: self.__task_to_job[v] for k, v in self.__scheduling_points[actual_execution_cycle].items()},
                next_scheduling_point - actual_execution_cycle, None)

    def on_jobs_activation(self, global_time: float, activation_time: float,
                           jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
        """
        Method to implement with the actual on job activation scheduler police.
        This method is the recommended place to detect the arrival of an aperiodic or sporadic task.

        :param jobs_id_tasks_ids: List[Identification of the job that have been activated,
         Identification of the task which job have been activated]
        :param global_time: Actual time in seconds since the simulation starts
        :param activation_time: Time where the activation was produced (It can be different from the global_time in the
         case that it doesn't adjust to a cycle end)
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        for job_id, task_id in jobs_id_tasks_ids:
            self.__task_to_job[task_id] = job_id

        return super().on_jobs_activation(global_time, activation_time, jobs_id_tasks_ids)
