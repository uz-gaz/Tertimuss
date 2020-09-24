from dataclasses import dataclass
from enum import Enum
from typing import Dict

import numpy


@dataclass
class SolidMaterial:
    """
    Isotropic thermal properties
    density: Density(Kg / m ^ 3)
    specificHeatCapacity: Specific heat capacity (J / Kg K)
    thermalConductivity: Thermal conductivity(W / m ºC)
    """
    density: float
    specificHeatCapacity: float
    thermalConductivity: float


@dataclass
class FluidEnvironmentProperties:
    """
    Specification of the environment

    environmentConvectionFactor: Convective Heat Transfer Coefficient (W / m^2 ºC)
    """
    heatTransferCoefficient: float


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
class ExternalTemperatureBoosterLocatedCube(LocatedCube):
    """
    Increase the temperature of all the cubes that are located inside the locatedCube by a rate of
    boostRate kelvin / second

    The integral of the cube temperature will be boostRate
    """
    boostRate: float


@dataclass
class InternalTemperatureBoosterLocatedCube(LocatedCube):
    """
    Increases the temperature of all cubes located in the locatedCube by a rate of
    (boostRateMultiplier * cube temperature) kelvin/second

    The integral of the cube temperature will be (boostRateMultiplier * cube temperature)
    """
    boostRateMultiplier: float


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
