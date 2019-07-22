class EnergyConsumptionProperties(object):
    def __init__(self, leakage_alpha: float = 0.001, leakage_delta: float = 0.1, dynamic_alpha: float = 1.52,
                 dynamic_beta: float = 0.08):
        """
        Core construction properties relatives to the energy consumption

        Dynamic power = dynamic_alpha * F^3 + dynamic_beta

        Static power = current temperature * 2 * leakage_delta + leakage_alpha

        To understand leakage_alpha and leakage_delta

        :param leakage_alpha: leakage_alpha
        :param leakage_delta: leakage_delta
        :param dynamic_alpha: dynamic_alpha
        :param dynamic_beta: dynamic_beta
        """
        # Convection properties
        self.leakage_delta: float = leakage_delta
        self.leakage_alpha: float = leakage_alpha

        # Heat generation properties
        self.dynamic_alpha: float = dynamic_alpha
        self.dynamic_beta: float = dynamic_beta
