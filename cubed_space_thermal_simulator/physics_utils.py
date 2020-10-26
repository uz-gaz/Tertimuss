from typing import List

from cubed_space_thermal_simulator import ExternalTemperatureBoosterLocatedCube, SolidMaterialLocatedCube, \
    TemperatureLocatedCube


def create_energy_applicator(located_cube: SolidMaterialLocatedCube, cube_edge_size: float,
                             watts_to_apply: float) -> ExternalTemperatureBoosterLocatedCube:
    """
    The resultant applicator will apply watts_to_apply watts distributed over the located_cube volume
    :param watts_to_apply: watts to apply
    :param cube_edge_size: edge size of each located cube cube
    :param located_cube: cube where the energy will be applied
    :return:
    """
    volume = (cube_edge_size ** 3) * (
            located_cube.dimensions.x * located_cube.dimensions.y * located_cube.dimensions.z)
    mass = located_cube.solidMaterial.density * volume
    specific_heat_capacity = located_cube.solidMaterial.specificHeatCapacity
    temperature_boost = watts_to_apply / (specific_heat_capacity * mass)
    return ExternalTemperatureBoosterLocatedCube(location=located_cube.location, dimensions=located_cube.dimensions,
                                                 boostRate=temperature_boost)


def transform_kelvin_temperature_located_cube_to_celsius(temperature_located_cube_list: List[TemperatureLocatedCube]) \
        -> List[TemperatureLocatedCube]:
    """Transform temperature located cube list in kelvin to celsius

    :param temperature_located_cube_list: Temperatures to transform
    :return: Temperatures in celsius
    """
    return [TemperatureLocatedCube(temperatureMatrix=i.temperatureMatrix - 273.15, dimensions=i.dimensions,
                                   location=i.location) for i in temperature_located_cube_list]
