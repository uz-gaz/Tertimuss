from typing import Optional

import scipy
from matplotlib import animation

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.templates.abstract_scheduler import SchedulerResult
import matplotlib.pyplot as plt


def draw_heat_matrix(global_specification: GlobalSpecification, global_model: GlobalModel,
                     scheduler_result: SchedulerResult, save_path: Optional[str] = None):
    """
    Draw heat matrix or save the simulation in file if save_path is not null
    :param global_specification: problem specification
    :param simulation_kernel: simulation kernel
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """
    temp = scheduler_result.temperature_map

    temp = scipy.transpose(temp)

    heat_map = []
    for actual_temp in temp:
        heat_map.append(__get_heat_matrix(actual_temp, global_specification))

    # Plot heat map
    min_temp = min(map(lambda x: scipy.amin(x), heat_map)) - 0.5
    max_temp = max(map(lambda x: scipy.amax(x), heat_map)) + 0.5

    fig, ax = plt.subplots()
    quad = ax.pcolormesh(heat_map[0], vmin=min_temp, vmax=max_temp)

    # Create colorbar
    cbar = ax.figure.colorbar(quad, ax=ax)
    cbar.ax.set_ylabel("Temperature ºC", rotation=-90, va="bottom")

    def animate(i):
        ax.set_title("Time: " + '%.2f' % scheduler_result.time_tcpn[i] + " seconds", loc='left')
        quad.set_array(heat_map[i].ravel())
        return quad

    anim = animation.FuncAnimation(fig, animate, frames=len(heat_map), interval=1, blit=False, repeat=False)

    # Save file or plot it
    if save_path is None:
        plt.show()
    else:
        # Set up formatting for the movie file
        writer = animation.FFMpegWriter(fps=30, metadata=dict(artist='TCPN Framework'), bitrate=1800)
        anim.save(save_path, writer=writer)


def __get_heat_matrix(temp, global_specification: GlobalSpecification) -> scipy.ndarray:
    mx = round(global_specification.cpu_specification.cpu_core_specification.x / global_specification.simulation_specification.step)
    my = round(global_specification.cpu_specification.cpu_core_specification.y / global_specification.simulation_specification.step)
    m = global_specification.cpu_specification.number_of_cores
    x = round(global_specification.cpu_specification.board_specification.x / global_specification.simulation_specification.step)
    y = round(global_specification.cpu_specification.board_specification.y / global_specification.simulation_specification.step)

    board_mat = scipy.zeros((x, y))
    cpus_mat = scipy.zeros((mx * m, my))

    for i in range(x):
        if i % 2 == 0:
            board_mat[i, :] = temp[y * i:y * (i + 1)]
        else:
            board_mat[i, :] = scipy.flip(temp[y * i:y * (i + 1)])

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
    time_u = scheduler_result.time_scheduler
    n = len(global_specification.tasks_specification.tasks)
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(m, sharex=True, num="CPU utilization")
    f.suptitle('CPU utilization')
    for i in range(m):
        axarr[i].set_title("CPU " + str(i))
        for j in range(n):
            axarr[i].plot(time_u, i_tau_disc[i * n + j], label="Task " + str(j), drawstyle='steps')
        axarr[i].legend(loc='best')

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


def plot_task_execution(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                        save_path: Optional[str] = None):
    """
    Plot task execution in each cpu
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    i_tau_disc = scheduler_result.scheduler_assignation
    time_u = scheduler_result.time_scheduler
    n = len(global_specification.tasks_specification.tasks)
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(n, sharex=True, num="Task execution")
    f.suptitle('Task execution')
    utilization_by_task = scipy.zeros((n, len(i_tau_disc[0])))

    total_steps_number = int(
        global_specification.tasks_specification.h / global_specification.simulation_specification.dt)
    deadline_by_task = scipy.zeros((n, total_steps_number))
    deadlines_time = [i * global_specification.simulation_specification.dt for i in range(total_steps_number)]

    for i in range(n):
        actual_deadline = int(
            global_specification.tasks_specification.tasks[i].t / global_specification.simulation_specification.dt)
        for j in range(len(i_tau_disc[0])):
            for k in range(m):
                utilization_by_task[i, j] += i_tau_disc[n * k + i, j]
        for j in range(total_steps_number):
            if j % actual_deadline == 0:
                deadline_by_task[i][j] = 1

    for j in range(n):
        axarr[j].set_title("Task " + str(j))
        axarr[j].plot(time_u, utilization_by_task[j], label="Execution", drawstyle='steps')
        axarr[j].plot(deadlines_time, deadline_by_task[j], label="Deadline", drawstyle='steps')
        axarr[j].legend(loc='best')

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


def plot_cpu_temperature(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                         save_path: Optional[str] = None):
    """
    Plot cpu temperature during the simulation
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    temperature_disc = scheduler_result.max_temperature_cores
    time_temp = scheduler_result.time_tcpn
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(m, sharex=True, num="CPU temperature")
    f.suptitle('CPU temperature')
    for i in range(m):
        axarr[i].set_title("CPU " + str(i))
        axarr[i].plot(time_temp, temperature_disc[i], label="Temperature", drawstyle='default')
        axarr[i].legend(loc='best')

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


def plot_accumulated_execution_time(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                                    save_path: Optional[str] = None):
    """
    Plot tasks accumulated execution time during the simulation
    :param global_specification: problem specification
    :param scheduler_result: result of scheduling
    :param save_path: path to save the simulation
    """

    mexec = scheduler_result.execution_time_scheduler
    mexec_tcpn = scheduler_result.execution_time_tcpn
    time_u = scheduler_result.time_scheduler
    time_step = scheduler_result.time_tcpn
    n = len(global_specification.tasks_specification.tasks)
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(m, n, num="Execution time")
    f.suptitle('Execution time')
    for i in range(m):
        for j in range(n):
            axarr[i][j].set_title("CPU " + str(i) + " task " + str(j))
            axarr[i][j].plot(time_u, mexec[i * n + j], label="mexec")
            axarr[i][j].plot(time_step, mexec_tcpn[i * n + j], label="mexec tcpn")
            axarr[i][j].legend(loc='best')

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
