from enum import Enum


class ThermalModelSelector(Enum):
    """
    Select thermal model type
    """
    THERMAL_MODEL_ENERGY_BASED = 0
    THERMAL_MODEL_FREQUENCY_BASED = 1
