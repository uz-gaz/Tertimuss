from enum import Enum

from ._thermal_model_energy import ThermalModelEnergy
from ._thermal_model_frequency import ThermalModelFrequencyAware


class ThermalModelSelector(Enum):
    """
    Select thermal model type
    """
    THERMAL_MODEL_ENERGY_BASED = ThermalModelEnergy
    THERMAL_MODEL_FREQUENCY_BASED = ThermalModelFrequencyAware
