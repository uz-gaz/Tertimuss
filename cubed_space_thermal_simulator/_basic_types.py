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
class SolidMaterial:
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
class LocatedCube:
    """
    Cube with location
    """
    dimensions: UnitDimensions
    location: UnitLocation


@dataclass
class TemperatureLocatedCube(LocatedCube):
    """
    Cube with temperature and location
    """
    temperatureMatrix: numpy.ndarray


@dataclass
class SolidMaterialLocatedCube(LocatedCube):
    """
    Cube with material and location
    """
    solidMaterial: SolidMaterial


@dataclass
class ExternalEnergyLocatedCube(LocatedCube):
    """
    Cube with location that generate energy. It generate (energy) amount of Joules in (period) seconds.
    """
    energy: float
    period: float


@dataclass
class InternalEnergyLocatedCube(LocatedCube):
    """
    Cube with location that generate energy that depends on the actual cube temperature.
    It increases the temperature of the cube by the actual temperature multiplied by (temperatureFactor) every
    (period) seconds.
    """
    temperatureFactor: float
    period: float


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
class FluidEnvironmentProperties:
    """
    Specification of the environment

    environmentConvectionFactor: Convection factor (W / m^2 ºC)
    environmentTemperature: Environment temperature (Kelvin)
    """
    environmentConvectionFactor: float
    environmentTemperature: float


class SimulationPrecision(Enum):
    """
    Simulation precision.

    Higher precision implies more resources consumption and more simulation time
    """
    HIGH_PRECISION = numpy.float64,
    MIDDLE_PRECISION = numpy.float32
