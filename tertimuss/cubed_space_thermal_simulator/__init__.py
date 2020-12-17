"""
==========================================
Cubed space thermal simulator
==========================================

This module provides a thermal simulator for a mesh defined by cubes. The simulation is done using the unit edge cube
 as the minimal simulation unit.
Each cube can be of a material in solid, liquid or gas state, however it assumes that state changes does not happens
 during the simulation.
Also, the following heat transfer rules are followed:

- Between two solid material cubes with a shared face only conduction happens
- Between two liquid/gas material cubes with a shared face

## Modules description

- _cubed_space.py: Main module. It exposes the model creation and model simulation functions.
- _result_plotter.py: Module used to plot the results of a simulation.
- physics_utils.py: Some utils that helps in the simulation definition.
- _basic_types.py: Defines types used in the module.
- materials_pack.py: Some materials physical properties definition.

## References:
For the thermal simulation is used the model proposed by:
- Desirena, Gaddiel & Vazquez, Carlos & Ramirez-Trevino, Antonio & Gomez-Gutierrez, David. (2014). Thermal modelling for
 temperature control in MPSoC's using Timed Continuous Petri Nets. 2014 IEEE Conference on Control Applications, CCA
 2014. 2135-2140. 10.1109/CCA.2014.6981618.
"""

from ._basic_types import *
from ._cubed_space import *
from ._result_plotter import *
