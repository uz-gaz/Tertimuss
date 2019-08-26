from enum import Enum

from main.core.tcpn_model_generator.ThermalModelEnergy import ThermalModelEnergy
from main.core.tcpn_model_generator.ThermalModelFrequency import ThermalModelFrequencyAware


class ThermalModelSelector(Enum):
    """
    Select thermal model type
    """
    THERMAL_MODEL_ENERGY_BASED = ThermalModelEnergy
    THERMAL_MODEL_FREQUENCY_BASED = ThermalModelFrequencyAware
