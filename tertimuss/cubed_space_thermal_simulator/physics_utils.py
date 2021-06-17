from typing import Tuple

from tertimuss.cubed_space_thermal_simulator._basic_types import SolidMaterial, Cuboid, TMExternal, CuboidTemperature


def create_energy_applicator(located_cube: Tuple[SolidMaterial, Cuboid], cube_edge_size: float,
                             watts_to_apply: float) -> TMExternal:
    """
    The resultant applicator will apply watts_to_apply watts distributed over the located_cube volume

    :param watts_to_apply: watts to apply in each region
    :param cube_edge_size: edge size of each located cuboid
    :param located_cube: cube where the energy will be applied
    :return:
    """
    volume = (cube_edge_size ** 3) * (
            located_cube[1].dimensions.x * located_cube[1].dimensions.y * located_cube[1].dimensions.z)
    mass = located_cube[0].density * volume
    specific_heat_capacity = located_cube[0].specificHeatCapacity
    temperature_boost = watts_to_apply / (specific_heat_capacity * mass)

    return TMExternal(cuboid=Cuboid(location=located_cube[1].location,
                                    dimensions=located_cube[1].dimensions),
                      boostRate=temperature_boost)


def transform_cuboid_temperature_kelvin_to_celsius(cuboid_temperature: CuboidTemperature) \
        -> CuboidTemperature:
    """Transform cuboid temperature in kelvin to celsius

    :param cuboid_temperature: Temperatures to transform
    :return: Temperatures in celsius
    """
    return CuboidTemperature(temperatureMatrix=cuboid_temperature.temperatureMatrix - 273.15)
