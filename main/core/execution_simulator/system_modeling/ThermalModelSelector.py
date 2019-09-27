from enum import Enum

from main.core.execution_simulator.system_modeling.ThermalModelEnergy import ThermalModelEnergy
from main.core.execution_simulator.system_modeling.ThermalModelFrequency import ThermalModelFrequencyAware


class ThermalModelSelector(Enum):
    """
    Select thermal model type
    """
    THERMAL_MODEL_ENERGY_BASED = ThermalModelEnergy
    THERMAL_MODEL_FREQUENCY_BASED = ThermalModelFrequencyAware
