from typing import List, Optional, Tuple

from ._basic_types import *


class CubedSpaceState(object):
    def __init__(self):
        pass


class CubedSpace(object):
    def __init__(self, material_cubes: List[Tuple[MaterialLocatedCube, int]], cube_edge_size: float,
                 environment_properties: EnvironmentProperties,
                 fixed_external_energy_application_points: List[Tuple[ExternalEnergyLocatedCube, int]],
                 fixed_internal_energy_application_points: List[Tuple[InternalEnergyLocatedCube, int]]):
        """
        This function create a cubedSpace

        :param material_cubes: List of cubes that conform the space. Each cube will have defined it's dimensions in unit
         units, the position in units and the thermal properties of the cube.
        :param cube_edge_size: Cubes' edge size in m (each cube will have the same edge size).
        :param environment_properties: The material that will be surrounded the cube will have these properties.
         This material won't change him temperature, however it will affect to the mesh temperature.
        :param fixed_external_energy_application_points: This parameter is only used with optimization purposes. If is
         not null, all of the elements of external_energy_application_points in the function apply_energy, must be in
         fixed_external_energy_application_points.
        :param fixed_internal_energy_application_points: This parameter is only used with optimization purposes. If is
         not null, all of the elements of internal_energy_application_points in the function apply_energy, must be in
         fixed_internal_energy_application_points.
        """
        pass

    def apply_energy(self, actual_state: CubedSpaceState,
                     external_energy_application_points: List[ExternalEnergyLocatedCube],
                     internal_energy_application_points: List[InternalEnergyLocatedCube],
                     amount_of_time: float) -> CubedSpaceState:
        """
        This function apply energy over the cubedSpace and return the transformed cubedSpace.

        :param external_energy_application_points: Points where the energy is applied. If the list is empty, none energy
         will be applied, however the energy transfer between cubes will be simulated. Each cube will have defined it's
         dimensions in unit units, it's position in units and the amount of energy to be applied.
        :param internal_energy_application_points: Points where the energy is applied. If the list is empty, none energy
         will be applied, however the energy transfer between cubes will be simulated. Each cube will have defined it's
         dimensions in unit units, it's position in units and the amount of energy to be applied.
        :param amount_of_time: Amount of time in seconds while the energy is being applied
        """
        pass

    def obtain_temperature(self, actual_state: CubedSpaceState, surrounded_cube: Optional[LocatedCube],
                           units: ThermalUnits) -> ModelTemperatureMatrix:
        """
        This function return the temperature in each cube of unit edge that conform the cubedSpace

        :param surrounded_cube: Only the temperature of the elements in this surrounded cube will be returned.
         By default, this cube is calculated as the cube that surrounds the rest of the cubes.
        :param units: Units to receive the temperature.
        """
        pass


def create_cubed_space(material_cubes: List[MaterialLocatedCube], cube_edge_size: float,
                       environment_properties: EnvironmentProperties,
                       external_energy_application_points: List[ExternalEnergyLocatedCube],
                       internal_energy_application_points: List[InternalEnergyLocatedCube]) \
        -> [CubedSpace, List[int], List[int], List[int]]:
    """
    This function create a cubedSpace

    :param material_cubes: List of cubes that conform the space. Each cube will have defined it's dimensions in unit
     units, the position in units and the thermal properties of the cube.
    :param cube_edge_size: Cubes' edge size in m (each cube will have the same edge size).
    :param environment_properties: The material that will be surrounded the cube will have these properties.
     This material won't change him temperature, however it will affect to the mesh temperature.
    :param external_energy_application_points: All of the elements of external_energy_application_points in the function
     apply_energy, must be in fixed_external_energy_application_points.
    :param internal_energy_application_points: All of the elements of internal_energy_application_points in the function
     apply_energy, must be in fixed_internal_energy_application_points.

     :return: List[int]: Id to refer to each material cube. It has the same size of material_cubes
              List[int]: Id to refer to each material cube. It has the same size of
               fixed_external_energy_application_points
              List[int]: Id to refer to each material cube. It has the same size of
               fixed_internal_energy_application_points
    """
    pass


def create_initial_state(cubed_space: CubedSpace, material_cubes_temperatures: Optional[List[Tuple[int, float]]],
                         default_temperature: float) -> CubedSpaceState:
    pass
