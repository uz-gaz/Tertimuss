from typing import List

from main.plot_generator.implementations.AccumulatedExecutionTimeDrawer import AccumulatedExecutionTimeDrawer
from main.plot_generator.implementations.ContextSwitchStatistics import ContextSwitchStatistics
from main.plot_generator.implementations.DynamicPowerConsumptionDrawer import DynamicPowerConsumptionDrawer
from main.plot_generator.implementations.ExecutionPercentageDrawer import ExecutionPercentageDrawer
from main.plot_generator.implementations.ExecutionPercentageStatistics import ExecutionPercentageStatistics
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
            "Context switch statistics": ContextSwitchStatistics(),
            "Cores maximum temperature": MaxCoreTemperatureDrawer(),
            "CPU heat evolution": HeatMatrixDrawer(),
            "Energy consumption": DynamicPowerConsumptionDrawer(),
            "Execution percentage": ExecutionPercentageDrawer(),
            "Execution percentage statistics": ExecutionPercentageStatistics(),
            "Frequency": FrequencyDrawer(),
            "Processor utilization": UtilizationDrawer(),
            "Task execution": TaskExecutionDrawer()
        }

        return output_definition.get(name)

    @staticmethod
    def select_output_naming(name: str) -> str:
        """
        Select output by name
        :param name: Name of the output
        :return:
        """
        output_definition = {
            "Accumulated execution time": "_accumulated_execution_time.png",
            "Energy consumption": "_energy_consumption.png",
            "Execution percentage": "_execution_percentage.png",
            "Frequency": "_frequency.png",
            "CPU heat evolution": "_heat_matrix.mp4",
            "Cores maximum temperature": "_cpu_temperature.png",
            "Task execution": "_task_execution.png",
            "Processor utilization": "_cpu_utilization.png"
        }

        return output_definition.get(name)

    @staticmethod
    def get_output_names_thermal() -> List[str]:
        return ["Accumulated execution time", "Energy consumption", "Execution percentage", "Frequency",
                "CPU heat evolution", "Cores maximum temperature", "Task execution", "Processor utilization"]

    @staticmethod
    def get_output_names_no_thermal() -> List[str]:
        return ["Accumulated execution time", "Execution percentage", "Frequency", "Task execution",
                "Processor utilization"]
