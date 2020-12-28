from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentSpecification:
    heat_transfer_coefficient: float  # Convective Heat Transfer Coefficient (W / m^2 ºC)
    temperature: float  # Environment temperature (ºK)
