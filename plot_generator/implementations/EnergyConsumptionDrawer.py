from typing import Optional, Dict

import scipy

from core.problem_specification.GlobalSpecification import GlobalSpecification
from core.schedulers.templates.abstract_scheduler import SchedulerResult
import matplotlib.pyplot as plt

from plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class EnergyConsumptionDrawer(AbstractResultDrawer):

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
        cls.__plot_energy_consumption(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_energy_consumption(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
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
