from cubed_space_thermal_simulator import FluidEnvironmentProperties, SolidMaterial


class AirFreeEnvironmentProperties(FluidEnvironmentProperties):
    """
    Free air properties
    src: https://www.sciencedirect.com/topics/engineering/convection-heat-transfer-coefficient
    """

    def __init__(self):
        super().__init__(heatTransferCoefficient=25)


class AirForcedEnvironmentProperties(FluidEnvironmentProperties):
    """
    Forced air properties
    src: https://www.sciencedirect.com/topics/engineering/convection-heat-transfer-coefficient
    """

    def __init__(self):
        super().__init__(heatTransferCoefficient=500)


class CooperSolidMaterial(SolidMaterial):
    """
    Cooper isotropic properties
    src: https://ieeexplore.ieee.org/document/6981618 (DOI 10.1109/CCA.2014.6981618)
    """

    def __init__(self):
        super().__init__(density=8933, specificHeatCapacities=385, thermalConductivity=400)


class SiliconSolidMaterial(SolidMaterial):
    """
    Silicon isotropic properties
    src: https://ieeexplore.ieee.org/document/6981618 (DOI 10.1109/CCA.2014.6981618)
    """

    def __init__(self):
        super().__init__(density=2330, specificHeatCapacities=712, thermalConductivity=148)
