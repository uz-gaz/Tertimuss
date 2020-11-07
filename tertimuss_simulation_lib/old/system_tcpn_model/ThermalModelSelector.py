from enum import Enum

from .ThermalModelEnergy import ThermalModelEnergy
from .ThermalModelFrequency import ThermalModelFrequencyAware


class ThermalModelSelector(Enum):
    """
    Select thermal model type
    """
    THERMAL_MODEL_ENERGY_BASED = ThermalModelEnergy
    THERMAL_MODEL_FREQUENCY_BASED = ThermalModelFrequencyAware
