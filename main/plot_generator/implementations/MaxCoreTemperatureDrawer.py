from typing import Optional, Dict

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
import matplotlib.pyplot as plt

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class MaxCoreTemperatureDrawer(AbstractResultDrawer):

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
        cls.__plot_cpu_temperature(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_cpu_temperature(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
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
