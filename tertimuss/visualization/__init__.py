"""
===================
Visualization tools
===================

This module contains the tools to generate visualizations of simulation results

This module provides the following functions:
- :function:`.generate_task_assignation_plot`
- :function:`.generate_job_assignation_plot`
- :function:`.generate_task_execution_plot`
- :function:`.generate_job_execution_plot`
- :function:`.generate_accumulate_execution_plot`
- :function:`.generate_job_accumulate_execution_plot`
- :function:`.generate_frequency_evolution_plot`
- :function:`.generate_component_hotspots_plot`
- :function:`.generate_board_temperature_evolution_2d_video`
- :function:`.generate_cpu_temperature_evolution_3d_video`
"""
from ._assignation_plot import generate_task_assignation_plot, generate_job_assignation_plot
from ._execution_plot import generate_task_execution_plot, generate_job_execution_plot
from ._accumulate_execution_plot import generate_accumulate_execution_plot, generate_job_accumulate_execution_plot
from ._frequency_evolution_plot import generate_frequency_evolution_plot
from ._component_hotspots_plot import generate_component_hotspots_plot
from ._cpu_temperature_plot import generate_board_temperature_evolution_2d_video, \
    generate_cpu_temperature_evolution_3d_video
