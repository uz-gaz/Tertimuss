from typing import Optional, Dict

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
import matplotlib.pyplot as plt

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class FrequencyDrawer(AbstractResultDrawer):

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
        cls.__plot_cpu_frequency(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_cpu_frequency(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                             save_path: Optional[str] = None):
        """
        Plot cpu temperature during the simulation
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """

        frequencies = scheduler_result.frequencies
        time_scheduler = scheduler_result.time_steps
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)
        f, axarr = plt.subplots(nrows=m, num="CPU frequency (Hz)")
        max_frequency = global_specification.cpu_specification.cores_specification.available_frequencies[-1]
        for i in range(m):
            axarr[i].set_title("$CPU_" + str(i + 1) + "$ frequency (Hz)")
            axarr[i].set_ylim(-0.2 * max_frequency, max_frequency * 1.2)
            axarr[i].plot(time_scheduler, frequencies[i], drawstyle='default')
            axarr[i].set_ylabel('frequency (Hz)')
            axarr[i].set_xlabel('time (s)')

        f.tight_layout()

        if save_path is None:
            plt.show()
        else:
            plt.savefig(save_path)

        plt.close(f)
