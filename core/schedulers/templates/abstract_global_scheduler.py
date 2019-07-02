import abc

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import Task
from core.schedulers.templates.abstract_scheduler import AbstractScheduler, SchedulerResult
from typing import List, Optional
from core.schedulers.utils.GlobalModelSolver import GlobalModelSolver
from output_generation.abstract_progress_bar import AbstractProgressBar


class GlobalSchedulerTask(Task):
    def __init__(self, task_specification: Task, task_id: int):
        super().__init__(task_specification.c, task_specification.t, task_specification.e)
        self.next_deadline = task_specification.t
        self.next_arrival = 0
        self.pending_c = task_specification.c
        self.instances = 0
        self.id = task_id


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
        n = len(global_specification.tasks_specification.tasks)
        cpu_utilization = sum(map(lambda a: a.c / a.t, global_specification.tasks_specification.tasks))

        # Exit program if can't be scheduled
        if cpu_utilization >= m:
            raise Exception("Error: Schedule is not feasible")

        # Tasks set
        tasks = [GlobalSchedulerTask(global_specification.tasks_specification.tasks[i], i) for i in
                 range(len(global_specification.tasks_specification.tasks))]

        # Number of steps in the simulation
        simulation_time_steps = int(round(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt))

        # Allocation of each task in each simulation step
        i_tau_disc = scipy.zeros((n * m, simulation_time_steps))

        # Time of each simulation step
        time_step = simulation_time_steps * [0]

        # Accumulated execution time
        m_exec = scipy.ndarray((n * m, simulation_time_steps))

        # Accumulated execution time tcpn
        m_exec_tcpn = scipy.ndarray((n * m, simulation_time_steps))

        # Temperature of cores in each step
        temperature_disc = []

        # Map with temperatures in each step
        temperature_map = []

        # Time where each temperature step have been obtained
        time_temp = []

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Actual cores temperature in each step
        cores_temperature = scipy.asarray(
            m * [global_specification.environment_specification.t_env]) if is_thermal_simulation else None

        # Run offline stage
        quantum = self.offline_stage(global_specification, global_model)

        # Number of steps in each quantum
        simulation_quantum_steps = int(round(
            quantum / global_specification.simulation_specification.dt))
        simulation_quantum_steps = 1 if simulation_quantum_steps == 0 else simulation_quantum_steps

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

            if quantum_q <= 0:
                # Get active task in this step
                # TODO: Check if the processor frequencies returned are in available ones
                active_task_id, next_quantum, next_core_frequencies = self.schedule_policy(time, tasks, m,
                                                                                           active_task_id,
                                                                                           clock_relative_frequencies,
                                                                                           cores_temperature)

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
                    if round(tasks[active_task_id[j]].pending_c, 5) > 0:
                        # Not end yet
                        tasks[active_task_id[j]].pending_c -= global_specification.simulation_specification.dt * \
                                                              clock_relative_frequencies[j]
                        w_alloc[active_task_id[j] + j * n] = 1
                        m_exec_step[active_task_id[j] + j * n] += global_specification.simulation_specification.dt

                    else:
                        # Ended
                        tasks[active_task_id[j]].instances += 1

                        tasks[active_task_id[j]].pending_c = tasks[active_task_id[j]].c

                        tasks[active_task_id[j]].next_arrival += tasks[active_task_id[j]].t
                        tasks[active_task_id[j]].next_deadline += tasks[active_task_id[j]].t

            m_exec_disc, board_temperature, cores_temperature, results_times = global_model_solver.run_step(
                w_alloc, time, clock_relative_frequencies)

            i_tau_disc[:, zeta_q] = w_alloc

            m_exec_tcpn[:, zeta_q] = m_exec_disc

            m_exec[:, zeta_q] = m_exec_step

            time_step[zeta_q] = time

            temperature_disc.append(cores_temperature)

            temperature_map.append(board_temperature)

            time_temp.append(results_times)

        time_step = scipy.asarray(time_step).reshape((-1, 1))

        if len(temperature_map) > 0:
            temperature_map = scipy.concatenate(temperature_map, axis=1)

        if len(time_temp) > 0:
            time_temp = scipy.concatenate(time_temp)

        if len(temperature_disc) > 0:
            temperature_disc = scipy.concatenate(temperature_disc, axis=1)

        return SchedulerResult(temperature_map, temperature_disc, time_step, time_temp, m_exec, m_exec_tcpn,
                               i_tau_disc, global_specification.simulation_specification.dt)

    def offline_stage(self, global_specification: GlobalSpecification, global_model: GlobalModel) -> float:
        """
        This method can be overridden with the offline stage scheduler tasks
        :param global_specification: Global specification
        :param global_model: Global model
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """
        return global_specification.simulation_specification.dt

    @abc.abstractmethod
    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
                        cores_frequency: List[float], cores_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[float]]]:
        """
        Method to implement with the actual scheduler police
        :param cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param tasks: tasks
        :param m: number of cores
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_temperature: temperature of each core
        :return: 1 - tasks to assign to cores in next step (task with id -1 is the idle task)
                 2 - next quantum size (if None, will be taken the quantum specified in the offline_stage)
                 3 - cores relatives frequencies for the next quantum (if None, will be taken the frequencies specified
                  in the problem specification)
        """
        pass
