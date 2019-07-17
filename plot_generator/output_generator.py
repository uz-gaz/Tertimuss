from typing import Optional

import scipy
from matplotlib import animation

from core.problem_specification.GlobalSpecification import GlobalSpecification
from core.schedulers.templates.abstract_scheduler import SchedulerResult
import matplotlib.pyplot as plt


def draw_heat_matrix(global_specification: GlobalSpecification, scheduler_result: SchedulerResult, show_board: bool,
                     show_cores: bool, save_path: Optional[str] = None):
    """
    Draw heat matrix or save the simulation in file if save_path is not null
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """
    temp = scheduler_result.temperature_map

    temp = scipy.transpose(temp)

    heat_map = []
    for actual_temp in temp:
        heat_map.append(__get_heat_matrix(actual_temp, global_specification, show_board, show_cores))

    # Plot heat map
    min_temp = min(map(lambda x: scipy.amin(x), heat_map)) - 0.5
    max_temp = max(map(lambda x: scipy.amax(x), heat_map)) + 0.5

    fig, ax = plt.subplots()
    quad = ax.pcolormesh(heat_map[0], vmin=min_temp, vmax=max_temp)

    # Create colorbar
    cbar = ax.figure.colorbar(quad, ax=ax)
    cbar.ax.set_ylabel("Temperature ºC", rotation=-90, va="bottom")

    def animate(i):
        ax.set_title("Time: " + '%.2f' % scheduler_result.time_steps[i] + " seconds", loc='left')
        quad.set_array(heat_map[i].ravel())
        return quad

    anim = animation.FuncAnimation(fig, animate, frames=len(heat_map), interval=1, blit=False, repeat=False)

    # Save file or plot it
    if save_path is None:
        plt.show()
    else:
        # writer = animation.FFMpegWriter(fps=30, metadata=dict(artist='TCPN Framework'), bitrate=1800)
        # FFMpegFileWriter
        writer = animation.FFMpegWriter(fps=30)
        anim.save(save_path, writer=writer)


def __get_heat_matrix(temp, global_specification: GlobalSpecification, show_board: bool, show_cores: bool) \
        -> scipy.ndarray:
    mx = round(
        global_specification.cpu_specification.cpu_core_specification.x / global_specification.simulation_specification.step)
    my = round(
        global_specification.cpu_specification.cpu_core_specification.y / global_specification.simulation_specification.step)
    m = global_specification.cpu_specification.number_of_cores
    x = round(
        global_specification.cpu_specification.board_specification.x / global_specification.simulation_specification.step)
    y = round(
        global_specification.cpu_specification.board_specification.y / global_specification.simulation_specification.step)

    board_mat = scipy.asarray([temp[y * i:y * (i + 1)] if i % 2 == 0 else scipy.flip(temp[y * i:y * (i + 1)]) for i in
                               range(x)]) if show_board \
        else scipy.full((x, y), global_specification.environment_specification.t_env)

    if show_cores:
        cpus_mat = scipy.zeros((mx * m, my))
        s = x * y
        for i in range(mx * m):
            cpus_mat[i, :] = temp[s + my * i:s + my * (i + 1)]

        for j in range(global_specification.cpu_specification.number_of_cores):
            i = global_specification.cpu_specification.cpu_origins[j]
            x_0: int = round(i.x / global_specification.simulation_specification.step)
            y_0: int = round(i.y / global_specification.simulation_specification.step)

            x_1: int = x_0 + mx
            y_1: int = y_0 + my

            board_mat[y_0:y_1, x_0:x_1] = cpus_mat[mx * j:mx * (j + 1)]

    return board_mat


def plot_cpu_utilization(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                         save_path: Optional[str] = None):
    """
    Plot cpu utilization
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    i_tau_disc = scheduler_result.scheduler_assignation
    time_u = scheduler_result.time_steps
    n_periodic = len(global_specification.tasks_specification.periodic_tasks)
    n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(nrows=m, num="CPU utilization")

    for i in range(m):
        axarr[i].set_title("$CPU_" + str(i + 1) + "$ utilization")
        for j in range(n_periodic):
            axarr[i].plot(time_u, i_tau_disc[i * (n_periodic + n_aperiodic) + j], label=r'$\tau_' + str(j + 1) + '$',
                          drawstyle='steps')
            axarr[i].set_ylabel('utilization')
            axarr[i].set_xlabel('time (s)')

        for j in range(n_aperiodic):
            axarr[i].plot(time_u, i_tau_disc[i * (n_periodic + n_aperiodic) + n_periodic + j],
                          label="Aperiodic " + str(j + 1),
                          drawstyle='steps')

        axarr[i].legend(loc='best')

    f.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

    plt.close(f)


def plot_task_execution(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                        save_path: Optional[str] = None):
    """
    Plot task execution in each cpu
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    i_tau_disc = scheduler_result.scheduler_assignation
    time_u = scheduler_result.time_steps
    n_periodic = len(global_specification.tasks_specification.periodic_tasks)
    n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(nrows=(n_periodic + n_aperiodic), num="Task execution")
    utilization_by_task = scipy.zeros(((n_periodic + n_aperiodic), len(i_tau_disc[0])))

    total_steps_number = int(
        global_specification.tasks_specification.h / global_specification.simulation_specification.dt)
    deadline_by_task = scipy.zeros(((n_periodic + n_aperiodic), total_steps_number))
    arrives_by_task = scipy.zeros((n_aperiodic, total_steps_number))
    deadlines_time = [i * global_specification.simulation_specification.dt for i in range(total_steps_number)]

    # Periodic tasks execution and deadlines
    for i in range(n_periodic):
        actual_deadline = int(
            global_specification.tasks_specification.periodic_tasks[
                i].t / global_specification.simulation_specification.dt)
        for j in range(len(i_tau_disc[0])):
            for k in range(m):
                utilization_by_task[i, j] += i_tau_disc[(n_periodic + n_aperiodic) * k + i, j]
        for j in range(total_steps_number):
            if j % actual_deadline == 0:
                deadline_by_task[i][j] = 1

    # Aperiodic tasks execution and deadlines
    for i in range(n_aperiodic):
        deadline = int(
            global_specification.tasks_specification.aperiodic_tasks[
                i].d / global_specification.simulation_specification.dt)
        arrive = int(
            global_specification.tasks_specification.aperiodic_tasks[
                i].a / global_specification.simulation_specification.dt)
        for j in range(len(i_tau_disc[0])):
            for k in range(m):
                utilization_by_task[i + n_periodic, j] += i_tau_disc[(n_periodic + n_aperiodic) * k + n_periodic + i, j]

        deadline_by_task[n_periodic + i][deadline] = 1
        arrives_by_task[i][arrive] = 1

    for j in range(n_periodic):
        axarr[j].set_title(r'$\tau_' + str(j + 1) + '$ execution')
        axarr[j].plot(time_u, utilization_by_task[j], label="Execution", drawstyle='steps')
        axarr[j].plot(deadlines_time, deadline_by_task[j], label="Deadline", drawstyle='steps')
        axarr[j].legend(loc='best')
        axarr[j].set_xlabel('time (s)')
        axarr[j].axes.get_yaxis().set_visible(False)

    for j in range(n_aperiodic):
        axarr[j + n_periodic].set_title("Aperiodic " + str(j))
        axarr[j + n_periodic].plot(time_u, utilization_by_task[n_periodic + j], label="Execution", drawstyle='steps')
        axarr[j + n_periodic].plot(deadlines_time, deadline_by_task[n_periodic + j], label="Deadline",
                                   drawstyle='steps')
        axarr[j + n_periodic].plot(deadlines_time, arrives_by_task[j], label="Arrive", drawstyle='steps')
        axarr[j + n_periodic].legend(loc='best')
        axarr[j].set_xlabel('time (s)')
        axarr[j].axes.get_yaxis().set_visible(False)

    f.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

    plt.close(f)


def plot_cpu_temperature(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                         save_path: Optional[str] = None):
    """
    Plot cpu temperature during the simulation
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    temperature_disc = scheduler_result.max_temperature_cores
    time_temp = scheduler_result.time_steps
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(nrows=m, num="CPU temperature")
    for i in range(m):
        axarr[i].set_title("$CPU_" + str(i + 1) + "$ temperature")
        axarr[i].plot(time_temp, temperature_disc[i], drawstyle='default')
        axarr[i].set_ylabel('temperature (ºC)')
        axarr[i].set_xlabel('time (s)')

    f.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

    plt.close(f)


def plot_energy_consumption(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                            save_path: Optional[str] = None):
    energy_consumption = scheduler_result.energy_consumption
    time_temp = scheduler_result.time_steps
    m = global_specification.cpu_specification.number_of_cores
    n_panels = m + 1
    f, axarr = plt.subplots(nrows=n_panels, num="CPU energy consumption by dynamic power")

    for i in range(m):
        axarr[i].set_title("$CPU_" + str(i + 1) + "$ energy consumed by dynamic power")
        axarr[i].plot(time_temp, energy_consumption[i], drawstyle='default')
        axarr[i].set_ylabel('energy (Watt)')
        axarr[i].set_xlabel('time (s)')

    axarr[-1].set_title("Total energy consumed by dynamic power ")
    axarr[-1].plot(time_temp, scipy.sum(energy_consumption, axis=0), drawstyle='default')
    axarr[-1].set_ylabel('energy (Watt)')
    axarr[-1].set_xlabel('time (s)')

    f.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

    plt.close(f)


def plot_accumulated_execution_time(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                                    save_path: Optional[str] = None):
    """
    Plot tasks accumulated execution time during the simulation
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    mexec = scheduler_result.execution_time_scheduler
    # mexec_tcpn = scheduler_result.execution_time_tcpn
    time_u = scheduler_result.time_steps
    # time_step = scheduler_result.time_tcpn
    n_periodic = len(global_specification.tasks_specification.periodic_tasks)
    n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(nrows=m, ncols=(n_periodic + n_aperiodic), num="Execution time")
    f.suptitle('Execution time')
    for i in range(m):
        for j in range(n_periodic):
            axarr[i][j].set_title("CPU " + str(i) + " task " + str(j))
            axarr[i][j].plot(time_u, mexec[i * (n_periodic + n_aperiodic) + j], label="mexec")
            # axarr[i][j].plot(time_step, mexec_tcpn[i * (n_periodic + n_aperiodic) + j], label="mexec tcpn")
            axarr[i][j].legend(loc='best')

    for i in range(m):
        for j in range(n_aperiodic):
            axarr[i][j + n_periodic].set_title("CPU " + str(i) + " aperiodic " + str(j))
            axarr[i][j + n_periodic].plot(time_u, mexec[i * (n_periodic + n_aperiodic) + n_periodic + j], label="mexec")
            # axarr[i][j + n_periodic].plot(time_step, mexec_tcpn[i * (n_periodic + n_aperiodic) + n_periodic + j],
            #                               label="mexec tcpn")
            axarr[i][j + n_periodic].legend(loc='best')

    f.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

    plt.close(f)


def plot_cpu_frequency(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                       save_path: Optional[str] = None):
    """
    Plot cpu temperature during the simulation
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    frequencies = scheduler_result.frequencies
    time_scheduler = scheduler_result.time_steps
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(nrows=m, sharex=True, num="CPU relative frequency")
    f.suptitle('CPU relative frequency')
    for i in range(m):
        axarr[i].set_title("CPU " + str(i))
        axarr[i].set_ylim(-0.2, 1.2)
        axarr[i].plot(time_scheduler, frequencies[i], label="Frequency", drawstyle='default')
        axarr[i].legend(loc='best')

    f.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

    plt.close(f)


def plot_task_execution_percentage(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                                   save_path: Optional[str] = None):
    """
    Plot task execution in each cpu
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    i_tau_disc = scheduler_result.scheduler_assignation
    frequencies = scheduler_result.frequencies

    n_periodic = len(global_specification.tasks_specification.periodic_tasks)
    n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

    frequencies_disc_f = scipy.concatenate(
        [scipy.repeat(i.reshape(1, -1), n_periodic + n_aperiodic, axis=0) for i in frequencies],
        axis=0)

    i_tau_disc = i_tau_disc * frequencies_disc_f

    hyperperiod = int(global_specification.tasks_specification.h / global_specification.simulation_specification.dt)

    ai = [int(global_specification.tasks_specification.h / i.t) for i in
          global_specification.tasks_specification.periodic_tasks]

    task_percentage_periodic = [scipy.zeros(i) for i in ai]

    task_percentage_aperiodic = []

    ci_p_dt = [int(round(i.c / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.periodic_tasks]

    di_p_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.periodic_tasks]

    ti_p_dt = [int(round(i.t / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.periodic_tasks]

    ci_a_dt = [int(round(i.c / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.aperiodic_tasks]

    ai_a_dt = [int(round(i.a / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.aperiodic_tasks]

    di_a_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.aperiodic_tasks]

    i_tau_disc_accond = scipy.zeros((n_periodic + n_aperiodic, len(i_tau_disc[0])))

    for i in range(global_specification.cpu_specification.number_of_cores):
        i_tau_disc_accond = i_tau_disc_accond + i_tau_disc[
                                                i * (n_periodic + n_aperiodic): (i + 1) * (n_periodic + n_aperiodic), :]

    for i in range(n_periodic):
        period_ranges = range(0, hyperperiod, ti_p_dt[i])
        task_percentage_periodic[i][:] = [sum(i_tau_disc_accond[i, j: j + di_p_dt[i]]) / ci_p_dt[i] for j in
                                          period_ranges]

    for i in range(n_aperiodic):
        execution_aperiodic = sum(i_tau_disc_accond[n_periodic + i, ai_a_dt[i]: di_a_dt[i]]) / ci_a_dt[i]
        task_percentage_aperiodic.append([execution_aperiodic])

    f, axarr = plt.subplots(nrows=(n_periodic + n_aperiodic), num="Task execution")
    f.suptitle('Task execution percentage in each period')

    for j in range(n_periodic):
        axarr[j].set_title("Task " + str(j))
        a_dibujar = task_percentage_periodic[j]
        axarr[j].bar(list(range(len(a_dibujar))), a_dibujar,
                     align='center')
        axarr[j].set_xticklabels([])

    for j in range(n_aperiodic):
        axarr[n_periodic + j].set_title("Aperiodic  " + str(j))
        axarr[n_periodic + j].bar([1], task_percentage_aperiodic[j],
                                  align='center')
        axarr[n_periodic + j].set_xticklabels([])

    f.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

    plt.close(f)
