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
class FluidEnvironment:
    """
    Specification of the environment
    """
    heatTransferCoefficient: float
    """Convective Heat Transfer Coefficient (W / m^2 ºC)"""


@dataclass
class Location:
    """
    Location in A units
    """
    x: int
    """Location in the x-axis"""

    y: int
    """Location in the y-axis"""

    z: int
    """Location in the z-axis"""


@dataclass
class Dimensions:
    """
    Dimensions in A units
    """
    x: int
    """Dimension in the x-axis"""

    y: int
    """Dimension in the y-axis"""

    z: int
    """Dimension in the z-axis"""


@dataclass
class Cuboid:
    """
    Cube with location in A units
    """
    dimensions: Dimensions
    """Dimensions of the cuboid"""

    location: Location
    """Location of the cuboid"""


@dataclass
class CuboidTemperature:
    """
    Temperature of a cuboid
    """
    temperatureMatrix: numpy.ndarray
    """3D matrix (x , y, z) that contains the temperature in each cube of the cuboid"""


@dataclass
class PhysicalCuboid:
    """
    Cuboid with physical properties
    """
    temperature: CuboidTemperature
    """Temperature of the cuboid"""

    material: SolidMaterial
    """Material of the cuboid"""

    cuboid: Cuboid
    """Cuboid"""


@dataclass
class TemperatureModifier:
    """
    Modify the temperature of the space enclosed in the cuboid
    """
    cuboid: Cuboid


@dataclass
class TMExternal(TemperatureModifier):
    """
    Increase the temperature of all the cubes that are located inside the locatedCube by a rate of
    boostRate kelvin / second
    """
    boostRate: float
    """The derivative of the cube temperature"""


@dataclass
class TMInternal(TemperatureModifier):
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
