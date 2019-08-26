from main.core.tcpn_model_generator.ThermalModelSelector import ThermalModelSelector


class TCPNModelSpecification(object):

    def __init__(self, thermal_model_selector: ThermalModelSelector):
        """
        Selection of the thermal model to use

        :param thermal_model_selector: Thermal model to use
        """
        self.thermal_model_selector: ThermalModelSelector = thermal_model_selector
