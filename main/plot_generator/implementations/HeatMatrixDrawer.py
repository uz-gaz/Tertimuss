from typing import Optional, Dict

import scipy
import matplotlib.pyplot as plt
from matplotlib import animation

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class HeatMatrixDrawer(AbstractResultDrawer):

    @classmethod
    def plot(cls, global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
             options: Dict[str, str]):
        """
        Plot results
        :param global_specification: Problem global specification
        :param scheduler_result: Result of the simulation
        :param options: Result drawer options

        Available options:
        save_path: path to save the simulation
        """
        cls.__draw_heat_matrix(global_specification, scheduler_result, options.get("show_board"),
                               options.get("show_cores"), options.get("save_path"))

    @classmethod
    def __draw_heat_matrix(cls, global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                           show_board: Optional[bool], show_cores: Optional[bool], save_path: Optional[str] = None):
        """
        Draw heat matrix or save the simulation in file if save_path is not null
        :param show_board: True if want to show the board
        :param show_cores: True if want to show cores
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """
        temp = scheduler_result.temperature_map

        temp = scipy.transpose(temp)

        heat_map = []
        for actual_temp in temp:
            heat_map.append(cls.__get_heat_matrix(actual_temp, global_specification, show_board, show_cores))

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
            writer = animation.FFMpegWriter(fps=30)
            anim.save(save_path, writer=writer)

    @staticmethod
    def __get_heat_matrix(temp, global_specification: GlobalSpecification, show_board: Optional[bool],
                          show_cores: Optional[bool]) -> scipy.ndarray:
        mx = round(
            global_specification.cpu_specification.cpu_core_specification.x /
            global_specification.simulation_specification.step)
        my = round(
            global_specification.cpu_specification.cpu_core_specification.y /
            global_specification.simulation_specification.step)
        m = global_specification.cpu_specification.number_of_cores
        x = round(
            global_specification.cpu_specification.board_specification.x /
            global_specification.simulation_specification.step)
        y = round(
            global_specification.cpu_specification.board_specification.y /
            global_specification.simulation_specification.step)

        board_mat = scipy.asarray(
            [temp[y * i:y * (i + 1)] if i % 2 == 0 else scipy.flip(temp[y * i:y * (i + 1)]) for i in
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
