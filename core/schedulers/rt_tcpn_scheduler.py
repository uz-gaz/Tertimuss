from typing import Optional

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from core.schedulers.utils.GlobalModelSolver import GlobalModelSolver
from core.schedulers.utils.lineal_programing_problem_for_scheduling import \
    solve_lineal_programing_problem_for_scheduling
from output_generation.abstract_progress_bar import AbstractProgressBar


class RtTCPNScheduler(AbstractScheduler):
    """
    Scheduler based on TCPN model presented in Desirena-Lopez et al.[2016]
    """

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification, global_model: GlobalModel,
                 progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:

        # True if simulation must save temperature
        is_thermal_simulation = global_model.enable_thermal_mode

        _, j_fsc_i, quantum, _ = solve_lineal_programing_problem_for_scheduling(
            global_specification.tasks_specification, global_specification.cpu_specification,
            global_specification.environment_specification,
            global_specification.simulation_specification, global_model)

        n = len(global_specification.tasks_specification.tasks)
        m = global_specification.cpu_specification.number_of_cores
        step = global_specification.simulation_specification.dt

        ti = [i.t for i in global_specification.tasks_specification.tasks]

        jobs = [int(i) for i in global_specification.tasks_specification.h / ti]

        diagonal = scipy.zeros((n, scipy.amax(jobs)))

        # Number of steps in the simulation
        simulation_time_steps = int(round(global_specification.tasks_specification.h / quantum))

        kd = 1
        sd_u = []
        for i in range(n):
            diagonal[i, 0: jobs[i]] = list(range(ti[i], global_specification.tasks_specification.h + 1, ti[i]))
            sd_u = scipy.union1d(sd_u, diagonal[i, 0: jobs[i]])

        sd_u = scipy.union1d(sd_u, [0])

        i_re_j = scipy.zeros(n * m)
        i_pr_j = scipy.zeros((m, n))

        zeta = 0
        time = 0

        sd = sd_u[kd]

        steps_in_quantum = int(round(quantum / step))

        # Allocation of each task in each simulation step
        i_tau_disc = scipy.zeros((n * m, simulation_time_steps * steps_in_quantum))

        # Time of each quantum
        time_step = steps_in_quantum * simulation_time_steps * [0]

        # Accumulated execution time
        m_exec = scipy.ndarray((n * m, steps_in_quantum * simulation_time_steps))

        # Accumulated execution time tcpn
        m_exec_tcpn = scipy.ndarray((n * m, steps_in_quantum * simulation_time_steps))

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

        m_busy = scipy.zeros(n * m)
        m_exec_accumulated = scipy.zeros(n * m)
        # time_z = scipy.ndarray((0, 1))
        # time_step = scipy.asarray([])
        # time_temp = scipy.ndarray((0, 1))
        # temperature_cont = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * n * m, 0))
        # temperature_disc = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * n * m, 0))
        # m_exec_history = scipy.ndarray((n * m, 0))
        # m_exec_tcpn_history = scipy.ndarray((n * m, 0))
        # mo_disc = simulation_kernel.mo
        # temperature_map = scipy.zeros((len(simulation_kernel.mo), 0))
        # mo = simulation_kernel.mo
        w_alloc = scipy.zeros(n * m)

        e_i_fsc_j = scipy.zeros(n * m)
        x1 = scipy.zeros(n * m)
        x2 = scipy.zeros(n * m)
        s = scipy.zeros(n * m)

        # Global model solver
        global_model_solver = GlobalModelSolver(global_model, global_specification)
        del global_model

        for zeta_q in range(simulation_time_steps):
            # Update progress
            if progress_bar is not None:
                progress_bar.update_progress(zeta_q / simulation_time_steps * 100)

            for time_q in range(steps_in_quantum):
                for j in range(m):
                    for i in range(n):
                        # Calculo del error, y la superficie para el sliding mode control
                        e_i_fsc_j[i + j * n] = j_fsc_i[i + j * n] * zeta - m_exec_step[i + j * n]

                        # Cambio de variables
                        x1[i + j * n] = e_i_fsc_j[i + j * n]
                        x2[i + j * n] = m_busy[i + j * n]  # m_bussy

                        # Superficie
                        s[i + j * n] = x1[i + j * n] - x2[i + j * n] + j_fsc_i[i + j * n]

                        # Control Para tareas temporal en cada procesador w_alloc control en I_tau
                        w_alloc[i + j * n] = (j_fsc_i[i + j * n] * scipy.sign(s[i + j * n]) + j_fsc_i[i + j * n]) / 2

                # mo_next, m_exec_step, m_busy, _, _, _, _ = solve_global_model(
                #     simulation_kernel.global_model,
                #     mo.reshape(-1),
                #     w_alloc,
                #     global_specification.environment_specification.t_env if is_thermal_simulation else 0,
                #     [time, time + step])
                #
                # mo = mo_next
                m_busy = w_alloc * step
                m_exec_step = m_exec_step + w_alloc * step
                # time_step = scipy.concatenate((time_step, scipy.asarray([time])))
                # m_exec_tcpn_history = scipy.concatenate((m_exec_tcpn_history, m_exec_step), axis=1)
                # time = time + step

            # DISCRETIZATION
            # Todas las tareas se expulsan de los procesadores
            # i_tau_disc[:, zeta_q] = 0

            # Se inicializa el conjunto ET de transiciones de tareas para el modelo discreto
            et = scipy.zeros((m, n), dtype=int)

            fsc = scipy.zeros(m * n)

            # Se calcula el remaining jobs execution Re_tau(j,i)
            for j in range(m):
                for i in range(n):
                    fsc[i + j * n] = j_fsc_i[i + j * n] * sd
                    i_re_j[i + j * n] = m_exec_step[i + j * n] - m_exec_accumulated[i + j * n]

                    if round(i_re_j[i + j * n], 4) > 0:
                        et[j, i] = i + 1

            for j in range(m):
                # Si el conjunto no es vacio por cada j-esimo CPU, entonces se procede a
                # calcular la prioridad de cada tarea a ser asignada
                if scipy.count_nonzero(et[j]) > 0:
                    # Prioridad es igual al marcado del lugar continuo menos el marcado del lugar discreto
                    i_pr_j[j, :] = j_fsc_i[j * n: j * n + n] * sd - m_exec_accumulated[j * n:j * n + n]

                    # Se ordenan de manera descendente por orden de prioridad,
                    # IndMaxPr contiene los indices de las tareas ordenado de mayor a
                    # menor prioridad
                    ind_max_pr = scipy.flip(scipy.argsort(i_pr_j[j, :]))

                    # Si en el vector ET(j,k) existe un cero entonces significa que en
                    # la posicion k la tarea no tine a Re_tau(j,k)>0 (es decir la tarea ya ejecuto lo que debía)
                    # entonces hay que incrementar a la siguiente posicion k+1 para tomar a la tarea de
                    # mayor prioridad
                    k = 0
                    while et[j, ind_max_pr[k]] == 0:
                        k = k + 1

                    # Se toma la tarea de mayor prioridad en el conjunto ET
                    ind_max_pr = et[j, ind_max_pr[k]] - 1

                    # si se asigna la procesador j la tarea de mayor prioridad IndMaxPr(1), entonces si en el
                    # conjunto ET para los procesadores restantes debe pasar que ET(k,IndMaxPr(1))=0,
                    # para evitar que las tareas se ejecuten de manera paralela
                    for k in range(m):
                        if j != k:
                            et[k, ind_max_pr] = 0

                    i_tau_disc[ind_max_pr + j * n,
                    zeta_q * steps_in_quantum: zeta_q * steps_in_quantum + steps_in_quantum] = steps_in_quantum * [1]

                    m_exec_accumulated[ind_max_pr + j * n] += quantum

            for i in range(steps_in_quantum):
                m_exec_disc, board_temperature, cores_temperature, results_times = global_model_solver.run_step(
                    i_tau_disc[:, zeta_q * steps_in_quantum + i].reshape(-1), zeta_q * quantum + i * step)
                m_exec_tcpn[:, zeta_q * steps_in_quantum + i] = m_exec_disc

                m_exec[:, zeta_q * steps_in_quantum + i] = m_exec_step

                time_step[zeta_q * steps_in_quantum + i] = zeta_q * quantum + i * step

                temperature_disc.append(cores_temperature)

                temperature_map.append(board_temperature)

                time_temp.append(results_times)

            if scipy.array_equal(round(zeta, 3), sd):
                kd = kd + 1
                if kd + 1 <= len(sd_u):
                    sd = sd_u[kd]

            zeta = zeta + quantum

        time_step = scipy.asarray(time_step).reshape((-1, 1))

        if len(temperature_map) > 0:
            temperature_map = scipy.concatenate(temperature_map, axis=1)

        if len(time_temp) > 0:
            time_temp = scipy.concatenate(time_temp)

        if len(temperature_disc) > 0:
            temperature_disc = scipy.concatenate(temperature_disc, axis=1)

        return SchedulerResult(temperature_map, temperature_disc, time_step, time_temp, m_exec, m_exec_tcpn,
                               i_tau_disc, global_specification.simulation_specification.dt)
