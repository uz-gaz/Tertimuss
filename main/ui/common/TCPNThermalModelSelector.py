from typing import List

from main.core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector


class TCPNThermalModelSelector(object):
    @staticmethod
    def select_tcpn_model(name: str) -> ThermalModelSelector:
        tcpn_model_definition = {
            "Energy based": ThermalModelSelector.THERMAL_MODEL_ENERGY_BASED,
            "Frequency based": ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED
        }
        return tcpn_model_definition.get(name)

    @staticmethod
    def get_tcpn_model_names() -> List[str]:
        return ["Energy based", "Frequency based"]
