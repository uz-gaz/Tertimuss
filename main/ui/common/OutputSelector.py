from main.plot_generator.implementations.AccumulatedExecutionTimeDrawer import AccumulatedExecutionTimeDrawer
from main.plot_generator.implementations.EnergyConsumptionDrawer import EnergyConsumptionDrawer
from main.plot_generator.implementations.ExecutionPercentageDrawer import ExecutionPercentageDrawer
from main.plot_generator.implementations.FrequencyDrawer import FrequencyDrawer
from main.plot_generator.implementations.HeatMatrixDrawer import HeatMatrixDrawer
from main.plot_generator.implementations.MaxCoreTemperatureDrawer import MaxCoreTemperatureDrawer
from main.plot_generator.implementations.TaskExecutionDrawer import TaskExecutionDrawer
from main.plot_generator.implementations.UtilizationDrawer import UtilizationDrawer
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class OutputSelector(object):
    @staticmethod
    def select_output(name: str) -> AbstractResultDrawer:
        """
        Select output by name
        :param name: Name of the output
        :return:
        """
        output_definition = {
            "Accumulated execution time": AccumulatedExecutionTimeDrawer(),
            "Energy consumption": EnergyConsumptionDrawer(),
            "Execution percentage": ExecutionPercentageDrawer(),
            "Frequency": FrequencyDrawer(),
            "CPU heat evolution": HeatMatrixDrawer(),
            "Cores maximum temperature": MaxCoreTemperatureDrawer(),
            "Task execution": TaskExecutionDrawer(),
            "Processor utilization": UtilizationDrawer()
        }

        return output_definition.get(name)
