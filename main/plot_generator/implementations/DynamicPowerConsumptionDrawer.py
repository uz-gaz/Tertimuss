from typing import Optional, Dict

import scipy

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult
import matplotlib.pyplot as plt

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class DynamicPowerConsumptionDrawer(AbstractResultDrawer):

    @classmethod
    def plot(cls, global_specification: GlobalSpecification, scheduler_result: SchedulingResult,
             options: Dict[str, str]):
        """
        Plot results
        :param global_specification: Problem global specification
        :param scheduler_result: Result of the simulation
        :param options: Result drawer options

        Available options:
        save_path: path to save the simulation
        """
        cls.__plot_dynamic_power_consumption(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_dynamic_power_consumption(global_specification: GlobalSpecification, scheduler_result: SchedulingResult,
                                         save_path: Optional[str] = None):
        """
        Plot the dynamic energy consumed by each core during the simulation
        :param global_specification: Problem global specification
        :param scheduler_result: Result of the simulation
        :param save_path: path to save the simulation
        :return:
        """
        energy_consumption = scheduler_result.energy_consumption
        time_temp = scheduler_result.time_steps
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)
        n_panels = m + 1
        f, axarr = plt.subplots(nrows=n_panels, num="CPU power consumption by dynamic power")

        for i in range(m):
            axarr[i].set_title("$CPU_" + str(i + 1) + "$ power consumed by dynamic power")
            axarr[i].plot(time_temp, energy_consumption[i], drawstyle='default')
            axarr[i].set_ylabel('power (Watt)')
            axarr[i].set_xlabel('time (s)')

        axarr[-1].set_title("Total power consumed by dynamic power ")
        axarr[-1].plot(time_temp, scipy.sum(energy_consumption, axis=0), drawstyle='default')
        axarr[-1].set_ylabel('power (Watt)')
        axarr[-1].set_xlabel('time (s)')

        f.tight_layout()

        if save_path is None:
            plt.show()
        else:
            plt.savefig(save_path)

        plt.close(f)
