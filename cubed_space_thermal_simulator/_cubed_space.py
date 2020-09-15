from typing import List, Optional, Tuple

import scipy.sparse

from ._basic_types import *


class CubedSpaceState(object):
    def __init__(self, places_mo_vector: numpy.ndarray):
        self.places_mo_vector = places_mo_vector


class CubedSpace(object):
    def __init__(self, material_cubes: Dict[int, SolidMaterialLocatedCube], cube_edge_size: float,
                 environment_properties: FluidEnvironmentProperties,
                 fixed_external_energy_application_points: Dict[int, ExternalEnergyLocatedCube],
                 fixed_internal_energy_application_points: Dict[int, InternalEnergyLocatedCube],
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
        material_cubes_dict = {}
        internal_conductivity_pre = []
        internal_conductivity_post = []
        internal_conductivity_lambda = []
        mo_cubes_size = []

        # First create internal conductivity for each material cube
        for material_cube_index, material_cube in material_cubes.items():
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
            pre = scipy.sparse.lil_matrix((p, t), dtype=simulation_precision.value)
            post = scipy.sparse.lil_matrix((p, t), dtype=simulation_precision.value)

            # All lambdas are equals
            lambda_vector = numpy.full(t, lambda_side, dtype=simulation_precision.value)

            # Create conductivity with horizontal adjacent
            for actual_z in range(z):
                for actual_y in range(y):
                    for actual_x in range(x - 1):
                        first_transition_index = 2 * (actual_z * y + actual_y * (x - 1) + actual_x)
                        second_transition_index = first_transition_index + 1

                        # First transition
                        pre[actual_z * y + actual_y * x + actual_x, first_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x + 1, first_transition_index] = 1

                        # Second transition
                        pre[actual_z * y + actual_y * x + actual_x + 1, second_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x, second_transition_index] = 1

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
                        pre[actual_z * y + actual_y * x + actual_x, first_transition_index] = 1
                        post[actual_z * y + (actual_y + 1) * x + actual_x, first_transition_index] = 1

                        # Second transition
                        pre[actual_z * y + (actual_y + 1) * x + actual_x, second_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x, second_transition_index] = 1

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
                        pre[actual_z * y + actual_y * x + actual_x, first_transition_index] = 1
                        post[(actual_z + 1) * y + actual_y * x + actual_x, first_transition_index] = 1

                        # Second transition
                        pre[(actual_z + 1) * y + actual_y * x + actual_x, second_transition_index] = 1
                        post[actual_z * y + actual_y * x + actual_x, second_transition_index] = 1

            # Save results
            mo_index[material_cube_index] = sum(mo_cubes_size)
            material_cubes_dict[material_cube_index] = material_cube
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
        self.__material_cubes_dict = material_cubes_dict

    def apply_energy(self, actual_state: CubedSpaceState,
                     external_energy_application_points: List[int],
                     internal_energy_application_points: List[int],
                     amount_of_time: float) -> CubedSpaceState:
        """
        This function apply energy over the cubedSpace and return the transformed cubedSpace.

        :param actual_state: 
        :param external_energy_application_points: Points where the energy is applied. If the list is empty, none energy
         will be applied, however the energy transfer between cubes will be simulated. Each cube will have defined it's
         dimensions in unit units, it's position in units and the amount of energy to be applied.
        :param internal_energy_application_points: Points where the energy is applied. If the list is empty, none energy
         will be applied, however the energy transfer between cubes will be simulated. Each cube will have defined it's
         dimensions in unit units, it's position in units and the amount of energy to be applied.
        :param amount_of_time: Amount of time in seconds while the energy is being applied
        """
        # TODO: Implement function
        return actual_state

    def obtain_temperature(self, actual_state: CubedSpaceState, units: ThermalUnits) -> List[TemperatureLocatedCube]:
        """
        This function return the temperature in each cube of unit edge that conform the cubedSpace

        :param actual_state:
        :param units: Units to receive the temperature.
        :return: List of temperature blocks
        """
        temperature_cubes = []

        for i, v in self.__mo_index.items():
            material_cube = self.__material_cubes_dict[i]
            number_of_occupied_places = material_cube.dimensions.x * material_cube.dimensions.y * material_cube.dimensions.z
            temperature_places = actual_state.places_mo_vector[v: v + number_of_occupied_places]
            temperature_cubes.append(
                TemperatureLocatedCube(material_cube.dimensions, material_cube.location, temperature_places))

        return temperature_cubes

    def create_initial_state(self, default_temperature: float,
                             material_cubes_temperatures: Optional[Dict[int, float]]) -> CubedSpaceState:
        places_temperature = []
        for i, v in self.__mo_index.items():
            material_cube = self.__material_cubes_dict[i]
            number_of_occupied_places = material_cube.dimensions.x * material_cube.dimensions.y * material_cube.dimensions.z
            local_places_temperature = numpy.ones(shape=(number_of_occupied_places))

            if material_cubes_temperatures is not None and material_cubes_temperatures.__contains__(i):
                places_temperature.append(local_places_temperature * material_cubes_temperatures[i])
            else:
                places_temperature.append(local_places_temperature * default_temperature)
        return CubedSpaceState(numpy.concatenate(places_temperature))
