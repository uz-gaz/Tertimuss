import abc

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import PeriodicTask, AperiodicTask
from core.schedulers.templates.abstract_scheduler import AbstractScheduler, SchedulerResult
from typing import List, Optional
from core.schedulers.utils.GlobalModelSolver import GlobalModelSolver
from output_generation.abstract_progress_bar import AbstractProgressBar


class GlobalSchedulerTask(object):
    def __init__(self, d: float, a: float, c: float, task_id: int):
        """
        Task information managed by the schedulers
        :param d: deadline
        :param a: arrival
        :param c: execution time
        :param task_id: id
        """
        self.next_deadline = d  # next task deadline in absolute seconds (since simulation start)
        self.next_arrival = a  # next task arrival in absolute seconds (since simulation start)
        self.pending_c = c  # pending execution seconds at base frequency
        # self.instances = 0  # Number of executed task instances
        self.id = task_id  # task id (always natural integer)


class GlobalSchedulerPeriodicTask(PeriodicTask, GlobalSchedulerTask):
    def __init__(self, task_specification: PeriodicTask, task_id: int):
        PeriodicTask.__init__(self, task_specification.c, task_specification.t, task_specification.d,
                              task_specification.e)
        GlobalSchedulerTask.__init__(self, task_specification.d, 0, task_specification.c, task_id)


class GlobalSchedulerAperiodicTask(AperiodicTask, GlobalSchedulerTask):
    def __init__(self, task_specification: AperiodicTask, task_id: int):
        AperiodicTask.__init__(self, task_specification.c, task_specification.a, task_specification.d,
                               task_specification.e)
        GlobalSchedulerTask.__init__(self, task_specification.d, task_specification.a, task_specification.c, task_id)


class AbstractGlobalScheduler(AbstractScheduler):
    """
    Abstract implementation of global scheduler (Custom Scheduler in original work).
    Method schedule_police must be implemented
    """

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification, global_model: GlobalModel,
                 progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:
        """

        :param global_model:
        :param progress_bar:
        :type global_specification: object
        """
        # True if simulation must save the temperature map
        is_thermal_simulation = global_model.enable_thermal_mode

        idle_task_id = -1
        m = global_specification.cpu_specification.number_of_cores
        n = len(global_specification.tasks_specification.aperiodic_tasks) + len(
            global_specification.tasks_specification.periodic_tasks)
        cpu_utilization = sum(map(lambda a: a.c / a.t, global_specification.tasks_specification.periodic_tasks)) + \
                          sum(map(lambda a: a.c / (a.d - a.c),
                                  global_specification.tasks_specification.aperiodic_tasks))

        # Exit program if can't be scheduled
        if cpu_utilization >= m:
            raise Exception("Error: Schedule is not feasible")

        # Tasks sets
        periodic_tasks = [GlobalSchedulerPeriodicTask(global_specification.tasks_specification.periodic_tasks[i], i)
                          for i in range(len(global_specification.tasks_specification.periodic_tasks))]
        aperiodic_tasks = [GlobalSchedulerAperiodicTask(global_specification.tasks_specification.aperiodic_tasks[i],
                                                        i + len(periodic_tasks))
                           for i in range(len(global_specification.tasks_specification.aperiodic_tasks))]

        tasks_set: List[GlobalSchedulerTask] = periodic_tasks + aperiodic_tasks  # The elements in this list will
        # point to the periodic_tasks and aperiodic_tasks elements

        # Number of steps in the simulation
        simulation_time_steps = int(round(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt))

        # Allocation of each task in each simulation step
        i_tau_disc = scipy.zeros((n * m, simulation_time_steps))

        # Time of each simulation step
        time_step = scipy.zeros((simulation_time_steps, 1))

        # Accumulated execution time
        m_exec = scipy.ndarray((n * m, simulation_time_steps))

        # Accumulated execution time tcpn
        m_exec_tcpn = scipy.ndarray((n * m, simulation_time_steps))

        # Max temperature of cores in each step
        max_temperature_cores = []

        # Map with temperatures in each step
        temperature_map = []

        # Time where each temperature step have been obtained
        time_temp = []

        # Actual cores temperature in each step
        cores_temperature = scipy.full(m, global_specification.environment_specification.t_env) \
            if is_thermal_simulation else None

        # Run offline stage
        quantum = self.offline_stage(global_specification, global_model, periodic_tasks, aperiodic_tasks)

        # Number of steps in each quantum
        simulation_quantum_steps = int(round(
            quantum / global_specification.simulation_specification.dt))
        simulation_quantum_steps = 1 if simulation_quantum_steps == 0 else simulation_quantum_steps

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Number of steps until next quantum
        quantum_q = 0

        # Global model solver
        global_model_solver = GlobalModelSolver(global_model, global_specification)
        del global_model

        # Actual set clock frequencies
        clock_relative_frequencies = global_specification.cpu_specification.clock_relative_frequencies

        # Active tasks
        active_task_id = m * [-1]

        for zeta_q in range(simulation_time_steps):
            # Update progress
            if progress_bar is not None:
                progress_bar.update_progress(zeta_q / simulation_time_steps * 100)

            # Update time
            time = zeta_q * global_specification.simulation_specification.dt

            # Manage aperiodic tasks
            if any([int(round(x.next_arrival / global_specification.simulation_specification.dt)) == zeta_q for x in
                    aperiodic_tasks]):
                periodic_arrives_list = [x.id for x in aperiodic_tasks if int(
                    round(x.next_arrival / global_specification.simulation_specification.dt)) == zeta_q]
                need_scheduled = self.aperiodic_arrive(time, periodic_tasks, active_task_id, clock_relative_frequencies,
                                                       cores_temperature, periodic_arrives_list)
                if need_scheduled:
                    # If scheduler need to be call
                    quantum_q = 0

            # Manage periodic tasks
            if quantum_q <= 0:
                # Get executable tasks in this interval
                executable_tasks = [actual_task for actual_task in tasks_set if
                                    int(round(
                                        actual_task.next_arrival / global_specification.simulation_specification.dt
                                    )) <= zeta_q and int(round(
                                        actual_task.pending_c / global_specification.simulation_specification.dt
                                    )) > 0]

                # Get active task in this step
                active_task_id, next_quantum, next_core_frequencies = self.schedule_policy(time, executable_tasks,
                                                                                           active_task_id,
                                                                                           clock_relative_frequencies,
                                                                                           cores_temperature)

                # Check if the processor frequencies returned are in available ones
                if next_core_frequencies is not None and all(
                        [x in global_specification.cpu_specification.clock_relative_frequencies for x in
                         next_core_frequencies]):
                    print("Warning: At least one of the frequencies selected on time", time, "is not available")

                quantum_q = int(round(next_quantum / global_specification.simulation_specification.dt)) - 1 \
                    if next_quantum is not None else simulation_quantum_steps - 1
                quantum_q = 0 if quantum_q < 0 else quantum_q

                clock_relative_frequencies = next_core_frequencies if next_core_frequencies is not None \
                    else global_specification.cpu_specification.clock_relative_frequencies

            else:
                quantum_q = quantum_q - 1

            # Allocation vector, form: task_1_in_cpu_1 ... task_n_in_cpu_1 ... task_1_in_cpu_m ... task_n_in_cpu_m
            # 1 for allocation and 0 for no allocation
            w_alloc = (n * m) * [0]

            for j in range(m):
                if active_task_id[j] != idle_task_id:
                    # Task not ended yet
                    tasks_set[
                        active_task_id[j]].pending_c -= global_specification.simulation_specification.dt * \
                                                        clock_relative_frequencies[j]
                    w_alloc[active_task_id[j] + j * n] = 1
                    m_exec_step[active_task_id[j] + j * n] += global_specification.simulation_specification.dt

                    if round(tasks_set[active_task_id[j]].pending_c, 5) <= 0:
                        if active_task_id[j] < len(periodic_tasks):
                            # It only manage the end of periodic tasks
                            # periodic_tasks[active_task_id[j]].instances += 1

                            tasks_set[active_task_id[j]].pending_c = periodic_tasks[active_task_id[j]].c

                            tasks_set[active_task_id[j]].next_arrival += periodic_tasks[active_task_id[j]].t
                            tasks_set[active_task_id[j]].next_deadline += periodic_tasks[active_task_id[j]].t
                        else:
                            # Aperiodic tasks only have to be to be executed once so arrive time and deadline will be
                            # higher than the hyperperiod

                            tasks_set[active_task_id[j]].next_arrival += global_specification.tasks_specification.h
                            tasks_set[active_task_id[j]].next_deadline += global_specification.tasks_specification.h

            m_exec_disc, board_temperature, cores_temperature, results_times = global_model_solver.run_step(
                w_alloc, time, clock_relative_frequencies)

            i_tau_disc[:, zeta_q] = w_alloc

            m_exec_tcpn[:, zeta_q] = m_exec_disc

            m_exec[:, zeta_q] = m_exec_step

            time_step[zeta_q, 0] = time

            time_temp.append(results_times)

            if is_thermal_simulation:
                max_temperature_cores.append(cores_temperature)

                temperature_map.append(board_temperature)

        if len(temperature_map) > 0:
            temperature_map = scipy.concatenate(temperature_map, axis=1)

        if len(time_temp) > 0:
            time_temp = scipy.concatenate(time_temp)

        if len(max_temperature_cores) > 0:
            max_temperature_cores = scipy.concatenate(max_temperature_cores, axis=1)

        return SchedulerResult(temperature_map, max_temperature_cores, time_step, time_temp, m_exec, m_exec_tcpn,
                               i_tau_disc, global_specification.simulation_specification.dt)

    @abc.abstractmethod
    def offline_stage(self, global_specification: GlobalSpecification, global_model: GlobalModel,
                      periodic_tasks: List[GlobalSchedulerPeriodicTask],
                      aperiodic_tasks: List[GlobalSchedulerAperiodicTask]) -> float:
        """
        Method to implement with the offline stage scheduler tasks
        :param aperiodic_tasks: list of aperiodic tasks with their assigned ids
        :param periodic_tasks: list of periodic tasks with their assigned ids
        :param global_specification: Global specification
        :param global_model: Global model
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """
        return global_specification.simulation_specification.dt

    @abc.abstractmethod
    def schedule_policy(self, time: float, executable_tasks: List[GlobalSchedulerTask], active_tasks: List[int],
                        actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[float]]]:
        """
        Method to implement with the actual scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param executable_tasks: actual tasks that can be executed ( c > 0 and arrive_time <= time)
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_max_temperature: temperature of each core
        :return: 1 - tasks to assign to cores in next step (task with id -1 is the idle task)
                 2 - next quantum size (if None, will be taken the quantum specified in the offline_stage)
                 3 - cores relatives frequencies for the next quantum (if None, will be taken the frequencies specified
                  in the problem specification)
        """
        pass

    @abc.abstractmethod
    def aperiodic_arrive(self, time: float, executable_tasks: List[GlobalSchedulerTask], active_tasks: List[int],
                         actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray],
                         aperiodic_task_ids: List[int]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param executable_tasks: actual tasks that can be executed ( c > 0 and arrive_time <= time)
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_max_temperature: temperature of each core
        :param aperiodic_task_ids: ids of the aperiodic tasks arrived
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        pass
