import scipy

from main.core.execution_simulator.system_simulator.SystemAperiodicTask import SystemAperiodicTask
from main.core.execution_simulator.system_simulator.SystemPeriodicTask import SystemPeriodicTask
from main.core.execution_simulator.system_simulator.SystemTask import SystemTask
from main.core.execution_simulator.system_modeling.GlobalModel import GlobalModel
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult
from typing import List, Optional
from main.core.execution_simulator.system_simulator.GlobalModelSolver import GlobalModelSolver
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from main.ui.common.AbstractProgressBar import AbstractProgressBar


class SystemSimulator(object):
    """
    System simulator
    """
    @staticmethod
    def simulate(global_specification: GlobalSpecification, global_model: GlobalModel,
                 scheduler: AbstractScheduler, progress_bar: Optional[AbstractProgressBar]) -> SchedulingResult:
        """
        Simulate problem
        :param global_specification: global specification of the problem
        :param global_model: global TCPN model
        :param scheduler: scheduler to use
        :param progress_bar: progress bar object if want to get simulation state feedback
        :return:
        """
        # True if simulation must save the temperature map
        is_thermal_simulation = global_model.enable_thermal_mode

        # Round a value and transform it to int
        def round_i(x: float) -> int:
            return int(round(x))

        idle_task_id = -1
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)
        n = len(global_specification.tasks_specification.aperiodic_tasks) + len(
            global_specification.tasks_specification.periodic_tasks)

        # Clock base frequency
        clock_base_frequency = global_specification.cpu_specification.cores_specification.available_frequencies[-1]

        # Tasks sets
        periodic_tasks = [SystemPeriodicTask(global_specification.tasks_specification.periodic_tasks[i], i)
                          for i in range(len(global_specification.tasks_specification.periodic_tasks))]
        aperiodic_tasks = [SystemAperiodicTask(global_specification.tasks_specification.aperiodic_tasks[i],
                                               i + len(periodic_tasks))
                           for i in range(len(global_specification.tasks_specification.aperiodic_tasks))]

        tasks_set: List[SystemTask] = periodic_tasks + aperiodic_tasks  # The elements in this list will
        # point to the periodic_tasks and aperiodic_tasks elements

        # Number of steps in the simulation
        simulation_time_steps = round_i(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt)

        # Allocation of each task in each simulation step
        i_tau_disc = scipy.ndarray((n * m, simulation_time_steps))

        # Time of each simulation step
        time_step = scipy.zeros(simulation_time_steps)

        # Accumulated execution time
        m_exec = scipy.ndarray((n * m, simulation_time_steps))

        # Accumulated execution time tcpn
        m_exec_tcpn = scipy.ndarray((n * m, simulation_time_steps))

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
        quantum = scheduler.offline_stage(global_specification, periodic_tasks, aperiodic_tasks)

        # Number of steps in each quantum
        simulation_quantum_steps = round_i(quantum / global_specification.simulation_specification.dt)
        simulation_quantum_steps = 1 if simulation_quantum_steps == 0 else simulation_quantum_steps

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Number of steps until next quantum
        quantum_q = 0

        # Global model solver
        global_model_solver = GlobalModelSolver(global_model, global_specification)
        del global_model

        # Actual set clock frequencies
        cores_operating_frequencies = global_specification.cpu_specification.cores_specification.operating_frequencies
        cores_available_frequencies = global_specification.cpu_specification.cores_specification.available_frequencies

        # Active tasks
        active_task_id = m * [-1]

        for zeta_q in range(simulation_time_steps):
            # Check if some deadline has arrived and update this task properties
            n_periodic = len(global_specification.tasks_specification.periodic_tasks)
            n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

            for j in range(n_periodic):
                if round_i(tasks_set[j].next_deadline / global_specification.simulation_specification.dt) == zeta_q:
                    # It only manage the end of periodic tasks
                    tasks_set[j].pending_c = periodic_tasks[j].c
                    tasks_set[j].next_arrival += periodic_tasks[j].t
                    tasks_set[j].next_deadline += periodic_tasks[j].t

            for j in range(n_aperiodic):
                if round_i(tasks_set[n_periodic + j].next_deadline /
                           global_specification.simulation_specification.dt) == zeta_q:
                    # It only manage the end of aperiodic tasks
                    tasks_set[n_periodic + j].next_arrival += global_specification.tasks_specification.h
                    tasks_set[n_periodic + j].next_deadline += global_specification.tasks_specification.h

            # Update progress
            if progress_bar is not None:
                progress_bar.update_progress(zeta_q / simulation_time_steps * 100)

            # Update time
            time = zeta_q * global_specification.simulation_specification.dt

            # Manage aperiodic tasks
            if any([round_i(x.next_arrival / global_specification.simulation_specification.dt) == zeta_q for
                    x in aperiodic_tasks]):
                # Has arrived a new aperiodic task
                aperiodic_arrives_list = [x for x in aperiodic_tasks if round_i(
                    x.next_arrival / global_specification.simulation_specification.dt) == zeta_q]
                need_scheduled = scheduler.aperiodic_arrive(time, aperiodic_arrives_list, cores_operating_frequencies,
                                                            cores_temperature if is_thermal_simulation else None)
                if need_scheduled:
                    # If scheduler need to be call
                    quantum_q = 0

            # Manage periodic tasks
            if quantum_q <= 0:
                # Get executable tasks in this interval
                executable_tasks = [actual_task for actual_task in tasks_set if
                                    round_i(
                                        actual_task.next_arrival / global_specification.simulation_specification.dt
                                    ) <= zeta_q and actual_task.pending_c > 0]

                available_tasks_to_execute = [actual_task.id for actual_task in executable_tasks] + [-1]

                # Get active task in this step
                active_task_id, next_quantum, next_core_frequencies = scheduler.schedule_policy(time, executable_tasks,
                                                                                                active_task_id,
                                                                                                cores_operating_frequencies,
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
                        [x in cores_available_frequencies for x in
                         next_core_frequencies]):
                    print("Warning: At least one frequency selected on time", time, "to execute is not available ones")

                quantum_q = round_i(next_quantum / global_specification.simulation_specification.dt) - 1 \
                    if next_quantum is not None else simulation_quantum_steps - 1
                quantum_q = 0 if quantum_q < 0 else quantum_q

                cores_operating_frequencies = next_core_frequencies if next_core_frequencies is not None \
                    else cores_operating_frequencies

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
                        active_task_id[j]].pending_c -= int(
                        cores_operating_frequencies[j] * global_specification.simulation_specification.dt)
                    w_alloc[active_task_id[j] + j * n] = 1
                    m_exec_step[active_task_id[j] + j * n] += global_specification.simulation_specification.dt

            m_exec_step_tcpn, board_temperature, cores_temperature, energy_consumption_actual = \
                global_model_solver.run_step(w_alloc, [i / clock_base_frequency for i in cores_operating_frequencies])

            i_tau_disc[:, zeta_q] = w_alloc

            m_exec[:, zeta_q] = m_exec_step

            m_exec_tcpn[:, zeta_q] = m_exec_step_tcpn

            time_step[zeta_q] = time

            core_frequencies[:, zeta_q] = cores_operating_frequencies

            if is_thermal_simulation:
                max_temperature_cores[:, zeta_q] = cores_temperature.reshape(-1)
                temperature_map[:, zeta_q] = board_temperature.reshape(-1)
                energy_consumption[:, zeta_q] = energy_consumption_actual

        return SchedulingResult(temperature_map, max_temperature_cores, time_step, m_exec, m_exec_tcpn, i_tau_disc,
                                core_frequencies, energy_consumption, global_specification.simulation_specification.dt)
