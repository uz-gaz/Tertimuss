from main.core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector


class TCPNModelSpecification(object):

    def __init__(self, thermal_model_selector: ThermalModelSelector):
        """
        Specification of some parameters of the simulation

        :param thermal_model_selector: Thermal model to use
        """
        self.thermal_model_selector: ThermalModelSelector = thermal_model_selector
