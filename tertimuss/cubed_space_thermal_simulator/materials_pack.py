from tertimuss.cubed_space_thermal_simulator._basic_types import FluidEnvironment, SolidMaterial


class FEAirFree(FluidEnvironment):
    """
    Free air properties
    src: https://www.sciencedirect.com/topics/engineering/convection-heat-transfer-coefficient
    """

    def __init__(self):
        super().__init__(heatTransferCoefficient=25)


class FEAirForced(FluidEnvironment):
    """
    Forced air properties
    src: https://www.sciencedirect.com/topics/engineering/convection-heat-transfer-coefficient
    """

    def __init__(self):
        super().__init__(heatTransferCoefficient=500)


class SMCooper(SolidMaterial):
    """
    Cooper isotropic properties
    src: https://ieeexplore.ieee.org/document/6981618 (DOI 10.1109/CCA.2014.6981618)
    """

    def __init__(self):
        super().__init__(density=8933, specificHeatCapacity=385, thermalConductivity=400)


class SMSilicon(SolidMaterial):
    """
    Silicon isotropic properties
    src: https://ieeexplore.ieee.org/document/6981618 (DOI 10.1109/CCA.2014.6981618)
    """

    def __init__(self):
        super().__init__(density=2330, specificHeatCapacity=712, thermalConductivity=148)
