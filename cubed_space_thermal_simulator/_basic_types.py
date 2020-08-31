from dataclasses import dataclass
from enum import Enum
from typing import Dict

import numpy


@dataclass
class UnitLocation:
    """
    Location in unit units
    """
    x: int
    y: int
    z: int


@dataclass
class UnitDimensions:
    """
    Dimensions in unit units
    """
    x: int
    y: int
    z: int


@dataclass
class Material:
    """
    Material definition
    density: Density(Kg / cm ^ 3)
    specificHeatCapacities: Specific heat capacities(J / Kg K)
    thermalConductivity: Thermal conductivity(W / m ºC)
    """
    density: float
    specificHeatCapacities: float
    thermalConductivity: float


@dataclass
class MaterialLocatedCube:
    """
    Cube with material and location
    """
    dimensions: UnitDimensions
    location: UnitLocation
    material: Material


@dataclass
class ExternalEnergyLocatedCube:
    """
    Cube with location that generate energy. It generate (energy) amount of Joules in (period) seconds.
    """
    dimensions: UnitDimensions
    location: UnitLocation
    energy: float
    period: float


@dataclass
class InternalEnergyLocatedCube:
    """
    Cube with location that generate energy that depends on the actual cube temperature.
    It increases the temperature of the cube by the actual temperature multiplied by (temperatureFactor) every
    (period) seconds.
    """
    dimensions: UnitDimensions
    location: UnitLocation
    temperatureFactor: float
    period: float


@dataclass
class LocatedCube:
    """
    Cube with location
    """
    dimensions: UnitDimensions
    location: UnitLocation


class ThermalUnits(Enum):
    """
    Thermal unit
    """
    KELVIN = 0
    CELSIUS = 1


@dataclass
class ModelTemperatureMatrix:
    """
    Model temperature matrix
    """
    temperatureMatrix: Dict[int, numpy.ndarray]


@dataclass
class EnvironmentProperties:
    """
    Specification of the environment

    environmentConvectionFactor: Convection factor (W / m^2 ºC)
    environmentTemperature: Environment temperature (Kelvin)
    """
    environmentConvectionFactor: float
    environmentTemperature: float
