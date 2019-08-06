import abc

import scipy
import math

from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerAperiodicTask import BaseSchedulerAperiodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerPeriodicTask import BaseSchedulerPeriodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerTask import BaseSchedulerTask
from main.core.tcpn_model_generator.GlobalModel import GlobalModel
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
from typing import List, Optional
from main.core.schedulers.utils.GlobalModelSolver import GlobalModelSolver
from main.ui.common.AbstractProgressBar import AbstractProgressBar


class AbstractBaseScheduler(AbstractScheduler, metaclass=abc.ABCMeta):
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

        # Round float to this decimal
        float_round = global_specification.simulation_specification.float_decimals_precision

        idle_task_id = -1
        m = len(global_specification.cpu_specification.cores_specification.cores_frequencies)
        n = len(global_specification.tasks_specification.aperiodic_tasks) + len(
            global_specification.tasks_specification.periodic_tasks)

        # Clock base frequency
        clock_base_frequency = global_specification.cpu_specification.cores_specification.cores_frequencies[-1]

        # Tasks sets
        periodic_tasks = [BaseSchedulerPeriodicTask(global_specification.tasks_specification.periodic_tasks[i], i,
                                                    clock_base_frequency)
                          for i in range(len(global_specification.tasks_specification.periodic_tasks))]
        aperiodic_tasks = [BaseSchedulerAperiodicTask(global_specification.tasks_specification.aperiodic_tasks[i],
                                                      i + len(periodic_tasks), clock_base_frequency)
                           for i in range(len(global_specification.tasks_specification.aperiodic_tasks))]

        tasks_set: List[BaseSchedulerTask] = periodic_tasks + aperiodic_tasks  # The elements in this list will
        # point to the periodic_tasks and aperiodic_tasks elements

        # Number of steps in the simulation
        simulation_time_steps = math.floor(round(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt, float_round))

        # Allocation of each task in each simulation step
        i_tau_disc = scipy.ndarray((n * m, simulation_time_steps))

        # Time of each simulation step
        time_step = scipy.zeros(simulation_time_steps)

        # Accumulated execution time
        m_exec = scipy.ndarray((n * m, simulation_time_steps))

        # Core frequencies in each step
        core_frequencies = scipy.ndarray((m, simulation_time_steps))

        # Max temperature of cores in each step
        max_temperature_cores = None

        # Map with temperatures in each step
        temperature_map = None

        # Actual cores temperature in each step
        cores_temperature = None

        # Actual cores energy consumption in each step
        energy_consumption = None

        if is_thermal_simulation:
            # Max temperature of cores in each step
            max_temperature_cores = scipy.ndarray((m, simulation_time_steps))

            # Map with temperatures in each step
            board_places = global_model.p_board
            cpus_places = global_model.p_one_micro * m
            temperature_map = scipy.ndarray((board_places + cpus_places, simulation_time_steps))

            # Actual cores temperature in each step
            cores_temperature = scipy.full(m, global_specification.environment_specification.t_env)

            # Actual cores energy consumption in each step
            energy_consumption = scipy.ndarray((m, simulation_time_steps))

        # Run offline stage
        quantum = self.offline_stage(global_specification, periodic_tasks, aperiodic_tasks)

        # Number of steps in each quantum
        simulation_quantum_steps = math.ceil(round(
            quantum / global_specification.simulation_specification.dt, float_round))
        simulation_quantum_steps = 1 if simulation_quantum_steps == 0 else simulation_quantum_steps

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Number of steps until next quantum
        quantum_q = 0

        # Global model solver
        global_model_solver = GlobalModelSolver(global_model, global_specification)
        del global_model

        # Actual set clock frequencies
        clock_relative_frequencies = [i / clock_base_frequency for i in
                                      global_specification.cpu_specification.cores_specification.cores_frequencies]
        clock_available_frequencies = [i / clock_base_frequency for i in
                                       global_specification.cpu_specification.cores_specification.available_frequencies]

        # Active tasks
        active_task_id = m * [-1]

        for zeta_q in range(simulation_time_steps):
            # Update progress
            if progress_bar is not None:
                progress_bar.update_progress(zeta_q / simulation_time_steps * 100)

            # Update time
            time = zeta_q * global_specification.simulation_specification.dt

            # Manage aperiodic tasks
            if any([math.ceil(
                    round(x.next_arrival / global_specification.simulation_specification.dt, float_round)) == zeta_q for
                    x in aperiodic_tasks]):
                aperiodic_arrives_list = [x for x in aperiodic_tasks if math.ceil(
                    round(x.next_arrival / global_specification.simulation_specification.dt, float_round)) == zeta_q]
                need_scheduled = self.aperiodic_arrive(time, aperiodic_arrives_list, clock_relative_frequencies,
                                                       cores_temperature if is_thermal_simulation else None)
                if need_scheduled:
                    # If scheduler need to be call
                    quantum_q = 0

            # Manage periodic tasks
            if quantum_q <= 0:
                # Get executable tasks in this interval
                executable_tasks = [actual_task for actual_task in tasks_set if
                                    math.ceil(round(
                                        actual_task.next_arrival / global_specification.simulation_specification.dt,
                                        float_round
                                    )) <= zeta_q and math.ceil(round(
                                        actual_task.pending_c / global_specification.simulation_specification.dt,
                                        float_round
                                    )) > 0]

                available_tasks_to_execute = [actual_task.id for actual_task in executable_tasks] + [-1]

                # Get active task in this step
                active_task_id, next_quantum, next_core_frequencies = self.schedule_policy(time, executable_tasks,
                                                                                           active_task_id,
                                                                                           clock_relative_frequencies,
                                                                                           cores_temperature if
                                                                                           is_thermal_simulation
                                                                                           else None)
                # Tasks selected by the scheduler to execute
                scheduler_selected_tasks = scipy.asarray(active_task_id)

                # Check if tasks returned are in available ones
                active_task_id = [actual_task if actual_task in available_tasks_to_execute else -1 for actual_task in
                                  active_task_id]

                if not scipy.array_equal(scheduler_selected_tasks, scipy.asarray(active_task_id)):
                    print("Warning: At least one task selected on time", time, "is not available")

                # Check if the processor frequencies returned are in available ones
                if next_core_frequencies is not None and not all(
                        [x in clock_available_frequencies for x in
                         next_core_frequencies]):
                    print("Warning: At least one frequency selected on time", time, "to execute is not available ones")

                quantum_q = math.ceil(
                    round(next_quantum / global_specification.simulation_specification.dt, float_round)) - 1 \
                    if next_quantum is not None else simulation_quantum_steps - 1
                quantum_q = 0 if quantum_q < 0 else quantum_q

                clock_relative_frequencies = next_core_frequencies if next_core_frequencies is not None \
                    else clock_relative_frequencies

            else:
                quantum_q = quantum_q - 1

            # Allocation vector, form: task_1_in_cpu_1 ... task_n_in_cpu_1 ... task_1_in_cpu_m ... task_n_in_cpu_m
            # 1 for allocation and 0 for no allocation
            w_alloc = (n * m) * [0]

            # Simulate execution
            for j in range(m):
                if active_task_id[j] != idle_task_id:
                    # Task is not idle
                    tasks_set[
                        active_task_id[j]].pending_c -= global_specification.simulation_specification.dt * \
                                                        clock_relative_frequencies[j]
                    w_alloc[active_task_id[j] + j * n] = 1
                    m_exec_step[active_task_id[j] + j * n] += global_specification.simulation_specification.dt

            _, board_temperature, cores_temperature, energy_consumption_actual, _ = global_model_solver.run_step(
                w_alloc, time, clock_relative_frequencies)

            i_tau_disc[:, zeta_q] = w_alloc

            m_exec[:, zeta_q] = m_exec_step

            time_step[zeta_q] = time

            core_frequencies[:, zeta_q] = clock_relative_frequencies

            if is_thermal_simulation:
                max_temperature_cores[:, zeta_q] = cores_temperature.reshape(-1)
                temperature_map[:, zeta_q] = board_temperature.reshape(-1)
                energy_consumption[:, zeta_q] = energy_consumption_actual

            # Check if some deadline has arrived and update this task properties
            n_periodic = len(global_specification.tasks_specification.periodic_tasks)
            n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

            for j in range(n_periodic):
                if math.ceil(round(tasks_set[j].next_deadline / global_specification.simulation_specification.dt,
                                   float_round)) == zeta_q:
                    # It only manage the end of periodic tasks
                    tasks_set[j].pending_c = periodic_tasks[j].c / clock_base_frequency
                    tasks_set[j].next_arrival += periodic_tasks[j].t
                    tasks_set[j].next_deadline += periodic_tasks[j].t

            for j in range(n_aperiodic):
                if math.ceil(round(tasks_set[
                                       n_periodic + j].next_deadline / global_specification.simulation_specification.dt,
                                   float_round)) == zeta_q:
                    # It only manage the end of aperiodic tasks
                    tasks_set[n_periodic + j].next_arrival += global_specification.tasks_specification.h
                    tasks_set[n_periodic + j].next_deadline += global_specification.tasks_specification.h

        return SchedulerResult(temperature_map, max_temperature_cores, time_step, m_exec,
                               i_tau_disc, core_frequencies, energy_consumption,
                               global_specification.simulation_specification.dt)

    @abc.abstractmethod
    def offline_stage(self, global_specification: GlobalSpecification,
                      periodic_tasks: List[BaseSchedulerPeriodicTask],
                      aperiodic_tasks: List[BaseSchedulerAperiodicTask]) -> float:
        """
        Method to implement with the offline stage scheduler tasks
        :param aperiodic_tasks: list of aperiodic tasks with their assigned ids
        :param periodic_tasks: list of periodic tasks with their assigned ids
        :param global_specification: Global specification
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """
        return global_specification.simulation_specification.dt

    @abc.abstractmethod
    def schedule_policy(self, time: float, executable_tasks: List[BaseSchedulerTask], active_tasks: List[int],
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
    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[BaseSchedulerTask],
                         actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        pass
