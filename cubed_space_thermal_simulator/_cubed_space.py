from typing import List, Optional, Tuple

import scipy.sparse

from ._basic_types import *


class CubedSpaceState(object):
    def __init__(self):
        pass


class CubedSpace(object):
    def __init__(self, material_cubes: List[Tuple[SolidMaterialLocatedCube, int]], cube_edge_size: float,
                 environment_properties: FluidEnvironmentProperties,
                 fixed_external_energy_application_points: List[Tuple[ExternalEnergyLocatedCube, int]],
                 fixed_internal_energy_application_points: List[Tuple[InternalEnergyLocatedCube, int]],
                 simulation_precision: SimulationPrecision):
        """
        This function create a cubedSpace

        :param material_cubes: List of cubes that conform the space. Each cube will have defined it's dimensions in unit
         units, the position in units and the thermal properties of the cube. Its assumed that all material cubes are
         metals
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
        mo_index = {}
        internal_conductivity_pre = []
        internal_conductivity_post = []
        internal_conductivity_lambda = []
        mo_cubes_size = []

        # First create internal conductivity for each material cube
        for material_cube, material_cube_index in material_cubes:
            # Parameters
            x: int = material_cube.dimensions.x
            y: int = material_cube.dimensions.y
            z: int = material_cube.dimensions.z

            rho: float = material_cube.solidMaterial.density
            k: float = material_cube.solidMaterial.thermalConductivity
            cp: float = material_cube.solidMaterial.specificHeatCapacities

            # Horizontal lambda and vertical lambda was refactored to achieve more precision
            # Horizontal lambda is equal to vertical lambda because sides are equals
            lambda_side = k / (rho * cp * (cube_edge_size ** 2))

            # Total number of PN places
            p: int = x * y * z

            # Total number of transitions -> One for each side in contact (two shared between two)
            # t = interactions in same z (4 * p - 2 * (x + y) * amount of z levels
            # + interactions between z levels (2 * x * y * (z - 1))
            # t: int = (4 * p - 2 * (x + y)) * z + 2 * x * y * (z - 1)
            t: int = 2 * (x - 1) * y * z + 2 * x * (y - 1) * z + 2 * x * y * (z - 1)

            # Each cube have been indexed by x, then by y and then by z
            # ie.
            # x = 3, y = 3, z = 2
            #
            # z_ind = 0    z_ind = 1
            #
            # 1 2 3        10 11 12
            # 4 5 6        13 14 15
            # 7 8 9        16 17 18
            pre = scipy.sparse.lil_matrix((p, t), dtype=simulation_precision)
            post = scipy.sparse.lil_matrix((p, t), dtype=simulation_precision)

            # All lambdas are equals
            lambda_vector = numpy.full(t, lambda_side, dtype=simulation_precision)

            # Create conductivity with horizontal adjacent
            for actual_z in range(z):
                for actual_y in range(y):
                    for actual_x in range(x - 1):
                        first_transition_index = 2 * (actual_z * y + actual_y * (x - 1) + actual_x)
                        second_transition_index = first_transition_index + 1

                        # First transition
                        pre[actual_z * y + actual_y * x + actual_x][first_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x + 1][first_transition_index] = 1

                        # Second transition
                        pre[actual_z * y + actual_y * x + actual_x + 1][second_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x][second_transition_index] = 1

            # Base index for vertical transitions
            base_transition_index_vertical = 2 * (x - 1) * y * z

            # Create conductivity with vertical adjacent
            for actual_z in range(z):
                for actual_y in range(y - 1):
                    for actual_x in range(x):
                        first_transition_index = base_transition_index_vertical + 2 * (
                                actual_z * (y - 1) + actual_y * x + actual_x)
                        second_transition_index = first_transition_index + 1

                        # First transition
                        pre[actual_z * y + actual_y * x + actual_x][first_transition_index] = 1
                        post[actual_z * y + (actual_y + 1) * x + actual_x][first_transition_index] = 1

                        # Second transition
                        pre[actual_z * y + (actual_y + 1) * x + actual_x][second_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x][second_transition_index] = 1

            # Base index for upper/lower transitions
            base_transition_index_upper_lower = 2 * (x - 1) * y * z + 2 * x * (y - 1) * z

            # Create conductivity with vertical upper and lower
            for actual_z in range(z - 1):
                for actual_y in range(y):
                    for actual_x in range(x):
                        first_transition_index = base_transition_index_upper_lower + 2 * (
                                actual_z * y + actual_y * x + actual_x)
                        second_transition_index = first_transition_index + 1

                        # First transition
                        pre[actual_z * y + actual_y * x + actual_x][first_transition_index] = 1
                        post[(actual_z + 1) * y + actual_y * x + actual_x][first_transition_index] = 1

                        # Second transition
                        pre[(actual_z + 1) * y + actual_y * x + actual_x][second_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x][second_transition_index] = 1

            # Save results
            mo_index[material_cube_index] = sum(mo_cubes_size)
            mo_cubes_size.append(p)
            internal_conductivity_pre.append(pre)
            internal_conductivity_post.append(post)
            internal_conductivity_lambda.append(lambda_vector)

        # TODO: Add energy generation
        # TODO: Add interaction between cuboids
        # TODO: Add convection

        # Create global pre, post and lambda
        self.__pre = scipy.sparse.block_diag(internal_conductivity_pre)
        self.__post = scipy.sparse.block_diag(internal_conductivity_post)
        self.__lambda_vector = numpy.concatenate(internal_conductivity_lambda)
        self.__mo_index = mo_index

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


def create_cubed_space(material_cubes: List[SolidMaterialLocatedCube], cube_edge_size: float,
                       environment_properties: FluidEnvironmentProperties,
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


def create_initial_state(cubed_space: CubedSpace, default_temperature: float,
                         material_cubes_temperatures: Optional[List[Tuple[int, float]]]) -> CubedSpaceState:
    pass
