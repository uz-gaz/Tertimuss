from typing import Optional

from core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector


class TCPNModelSpecification(object):
    """
    Specification of some parameters of the simulation
    """

    def __init__(self, thermal_model_selector: Optional[ThermalModelSelector]):
        """

        :param thermal_model_selector: Thermal model to use
        """
        self.thermal_model_selector = thermal_model_selector
