import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.abstract_scheduler import SchedulerResult
import matplotlib.pyplot as plt


def draw_heat_matrix(global_specification: GlobalSpecification, simulation_kernel: SimulationKernel,
                     scheduler_result: SchedulerResult):
    temp = simulation_kernel.global_model.s_thermal.dot(scheduler_result.m)

    temp = scipy.transpose(temp)

    heat_map = []
    for actual_temp in temp:
        heat_map.append(get_heat_matrix(actual_temp, global_specification))

    plot_heat_map(heat_map)


def get_heat_matrix(temp, global_specification: GlobalSpecification) -> scipy.ndarray:
    mx = int(global_specification.cpu_specification.cpu_core.x / global_specification.simulation_specification.step)
    my = int(global_specification.cpu_specification.cpu_core.y / global_specification.simulation_specification.step)
    m = global_specification.cpu_specification.number_of_cores
    x = int(global_specification.cpu_specification.board.x / global_specification.simulation_specification.step)
    y = int(global_specification.cpu_specification.board.y / global_specification.simulation_specification.step)

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


def plot_heat_map(heat_map):
    sleep_between_frames = 0.1

    min_temp = min(map(lambda x: scipy.amin(x), heat_map)) - 0.5
    max_temp = max(map(lambda x: scipy.amax(x), heat_map)) + 0.5

    plt.ion()

    fig, ax = plt.subplots()

    im = ax.imshow(heat_map[0], cmap='viridis', vmax=max_temp, vmin=min_temp)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Temperature", rotation=-90, va="bottom")

    plt.pause(sleep_between_frames)

    for i in range(len(heat_map) - 1):
        ax.imshow(heat_map[i], cmap='viridis', vmax=max_temp, vmin=min_temp)
        plt.pause(sleep_between_frames)


def plot_cpu_utilization(global_specification: GlobalSpecification, scheduler_result: SchedulerResult):
    # TODO: Revisar esto
    i_tau_disc = scheduler_result.sch_oldtfs
    time_z = scheduler_result.timez
    n = len(global_specification.tasks_specification.tasks)
    m = global_specification.cpu_specification.number_of_cores
    f, axarr = plt.subplots(m, sharex=True)
    f.suptitle('CPU utilization')
    for i in range(m):
        for j in range(n):
            axarr[i].plot(i_tau_disc[i * n + j])
    plt.show()
    plt.pause(10)
