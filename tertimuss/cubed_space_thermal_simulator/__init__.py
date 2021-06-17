"""
=============================
Cubed space thermal simulator
=============================

This library  provides a thermal simulator for a mesh defined by cubes. The simulation is done using the
**unit edge cube** as the minimal simulation unit.

Each cube can be of a material in solid, liquid or gas state, however it assumes that state changes does not happen
during the simulation.

Also, the following heat transfer rules are followed:

- Between two solid material cubes with a shared face, only conduction happens
- Between two liquid/gas material cubes with a shared face, conduction and convection happens
- Between a solid material, and a liquid/gas material cubes with a shared face, conduction and convection happens

This thermal model is based on the model presented in [Desirena]_.

.. [Desirena] Desirena, Gaddiel & Vazquez, Carlos & Ramirez-Trevino, Antonio & Gomez-Gutierrez, David. (2014). Thermal
modelling for temperature control in MPSoC's using Timed Continuous Petri Nets. 2014 IEEE Conference on Control
Applications, CCA 2014. 2135-2140. 10.1109/CCA.2014.6981618.

This module provides the following functions related to the thermal model:
- :function:`.obtain_min_temperature`
- :function:`.obtain_max_temperature`

This module provides the following functions that allows the visualization of the thermal model:
- :function:`.plot_3d_heat_map_temperature`
- :function:`.generate_video_3d_heat_map`
- :function:`.plot_2d_heat_map`
- :function:`.generate_video_2d_heat_map`

It also exposes the following classes:
- :class:`.Location`
- :class:`.Dimensions`
- :class:`.Cuboid`
- :class:`.CuboidTemperature`
- :class:`.TMInternal`
- :class:`.TMExternal`
- :class:`.ThermalUnits`
- :class:`.PhysicalCuboid`
- :class:`.SolidMaterial`
- :class:`.FluidEnvironment`
- :class:`.Model`
- :class:`.SimulationState`
"""

from ._basic_types import Location, Dimensions, Cuboid, CuboidTemperature, \
    TMInternal, TMExternal, ThermalUnits, \
    PhysicalCuboid, SolidMaterial, FluidEnvironment
from ._cubed_space import Model, SimulationState, obtain_min_temperature, obtain_max_temperature
from ._result_plotter import plot_3d_heat_map_temperature, generate_video_3d_heat_map, plot_2d_heat_map, \
    generate_video_2d_heat_map
