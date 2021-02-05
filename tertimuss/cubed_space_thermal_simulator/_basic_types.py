from dataclasses import dataclass
from enum import Enum
from typing import Dict

import numpy


@dataclass
class SolidMaterial:
    """
    Isotropic thermal properties'
    """
    density: float
    """density: Density(Kg / m ^ 3)"""

    specificHeatCapacity: float
    """Specific heat capacity (J / Kg K)"""

    thermalConductivity: float
    """Thermal conductivity(W / m ºC)"""


@dataclass
class FluidEnvironmentProperties:
    """
    Specification of the environment
    """
    heatTransferCoefficient: float
    """Convective Heat Transfer Coefficient (W / m^2 ºC)"""


@dataclass
class UnitLocation:
    """
    Location in unit units
    """
    x: int
    """Location in the x-axis"""

    y: int
    """Location in the y-axis"""

    z: int
    """Location in the z-axis"""


@dataclass
class UnitDimensions:
    """
    Dimensions in unit units
    """
    x: int
    """Dimension in the x-axis"""

    y: int
    """Dimension in the y-axis"""

    z: int
    """Dimension in the z-axis"""


@dataclass
class LocatedCube:
    """
    Cube with location
    """
    dimensions: UnitDimensions
    """Dimensions of the cuboid"""

    location: UnitLocation
    """Location of the cuboid"""


@dataclass
class TemperatureLocatedCube(LocatedCube):
    """
    Cube with temperature and location
    """
    temperatureMatrix: numpy.ndarray
    """Temperature in each unit cube of the cuboid"""


@dataclass
class ExternalTemperatureBoosterLocatedCube(LocatedCube):
    """
    Increase the temperature of all the cubes that are located inside the locatedCube by a rate of
    boostRate kelvin / second
    """
    boostRate: float
    """The derivative of the cube temperature"""


@dataclass
class InternalTemperatureBoosterLocatedCube(LocatedCube):
    """
    Increases the temperature of all cubes located in the locatedCube by a rate of
    (boostRateMultiplier * cube temperature) kelvin/second
    """
    boostRateMultiplier: float
    """The derivative of the cube temperature multiplier"""


class ThermalUnits(Enum):
    """
    Thermal unit
    """
    KELVIN = 0
    """Kelvin degrees"""

    CELSIUS = 1
    """Celsius degrees"""


@dataclass
class ModelTemperatureMatrix:
    """
    Model temperature matrix
    """
    temperatureMatrix: Dict[int, numpy.ndarray]
    """Temperature in each cuboid of the mesh"""
