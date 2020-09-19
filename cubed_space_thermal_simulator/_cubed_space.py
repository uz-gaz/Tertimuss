from typing import List, Optional, Tuple

import scipy.sparse

from tcpn_simulator import AbstractTCPNSimulator, TCPNSimulatorVariableStepEuler
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
                        first_transition_index = 2 * (actual_z * y * (x - 1) + actual_y * (x - 1) + actual_x)
                        second_transition_index = first_transition_index + 1

                        # First transition
                        pre[actual_z * y * x + actual_y * x + actual_x, first_transition_index] = 1
                        post[actual_z * y * x + actual_y * x + actual_x + 1, first_transition_index] = 1

                        # Second transition
                        pre[actual_z * y * x + actual_y * x + actual_x + 1, second_transition_index] = 1
                        post[actual_z * y * x + actual_y * x + actual_x, second_transition_index] = 1

            # Base index for vertical transitions
            base_transition_index_vertical = 2 * (x - 1) * y * z

            # Create conductivity with vertical adjacent
            for actual_z in range(z):
                for actual_y in range(y - 1):
                    for actual_x in range(x):
                        first_transition_index = base_transition_index_vertical + 2 * (
                                actual_z * (y - 1) * x + actual_y * x + actual_x)
                        second_transition_index = first_transition_index + 1

                        # First transition
                        pre[actual_z * y * x + actual_y * x + actual_x, first_transition_index] = 1
                        post[actual_z * y * x + (actual_y + 1) * x + actual_x, first_transition_index] = 1

                        # Second transition
                        pre[actual_z * y * x + (actual_y + 1) * x + actual_x, second_transition_index] = 1
                        post[actual_z * y * x + actual_y * x + actual_x, second_transition_index] = 1

            # Base index for upper/lower transitions
            base_transition_index_upper_lower = 2 * (x - 1) * y * z + 2 * x * (y - 1) * z

            # Create conductivity with vertical upper and lower
            for actual_z in range(z - 1):
                for actual_y in range(y):
                    for actual_x in range(x):
                        first_transition_index = base_transition_index_upper_lower + 2 * (
                                actual_z * y * x + actual_y * x + actual_x)
                        second_transition_index = first_transition_index + 1

                        # First transition
                        pre[actual_z * y * x + actual_y * x + actual_x, first_transition_index] = 1
                        post[(actual_z + 1) * y * x + actual_y * x + actual_x, first_transition_index] = 1

                        # Second transition
                        pre[(actual_z + 1) * y * x + actual_y * x + actual_x, second_transition_index] = 1
                        post[actual_z * y * x + actual_y * x + actual_x, second_transition_index] = 1

            # Save results
            mo_index[material_cube_index] = sum(mo_cubes_size)
            material_cubes_dict[material_cube_index] = material_cube
            mo_cubes_size.append(p)
            internal_conductivity_pre.append(pre)
            internal_conductivity_post.append(post)
            internal_conductivity_lambda.append(lambda_vector)

        # Add interaction between cuboids
        mo_size = sum(mo_cubes_size)

        external_conductivity_pre = []
        external_conductivity_post = []
        external_conductivity_lambda = []

        for material_cube_a_index, material_cube_a in material_cubes.items():
            for material_cube_b_index, material_cube_b in material_cubes.items():
                if material_cube_a_index != material_cube_b_index:
                    places_in_touch = self.__obtain_places_in_touch(material_cube_a, mo_index[material_cube_a_index],
                                                                    material_cube_b, mo_index[material_cube_b_index])
                    for place_a, place_b in places_in_touch:
                        pre = scipy.sparse.lil_matrix((mo_size, 2), dtype=simulation_precision.value)
                        post = scipy.sparse.lil_matrix((mo_size, 2), dtype=simulation_precision.value)

                        # Transition 1, from A -> B
                        pre[place_a, 0] = 1
                        post[place_b, 0] = (material_cube_a.solidMaterial.density
                                            * material_cube_a.solidMaterial.specificHeatCapacities) / \
                                           (material_cube_b.solidMaterial.density
                                            * material_cube_b.solidMaterial.specificHeatCapacities)

                        # Transition 2, from B -> A
                        pre[place_b, 1] = 1
                        post[place_a, 1] = (material_cube_b.solidMaterial.density
                                            * material_cube_b.solidMaterial.specificHeatCapacities) / \
                                           (material_cube_a.solidMaterial.density
                                            * material_cube_a.solidMaterial.specificHeatCapacities)

                        # All lambdas are equals
                        lambda_vector = numpy.zeros(shape=2, dtype=simulation_precision.value)

                        # Calculate lambda from A -> B
                        lambda_vector[0] = (material_cube_a.solidMaterial.thermalConductivity
                                            * material_cube_b.solidMaterial.thermalConductivity) / \
                                           (material_cube_a.solidMaterial.density
                                            * material_cube_a.solidMaterial.specificHeatCapacities
                                            * (material_cube_a.solidMaterial.thermalConductivity
                                               + material_cube_b.solidMaterial.thermalConductivity)
                                            * (cube_edge_size ** 2))

                        # Calculate lambda from B -> A
                        lambda_vector[1] = (material_cube_a.solidMaterial.thermalConductivity
                                            * material_cube_b.solidMaterial.thermalConductivity) / \
                                           (material_cube_b.solidMaterial.density
                                            * material_cube_b.solidMaterial.specificHeatCapacities
                                            * (material_cube_a.solidMaterial.thermalConductivity
                                               + material_cube_b.solidMaterial.thermalConductivity)
                                            * (cube_edge_size ** 2))

                        # Append to global values
                        external_conductivity_pre.append(pre)
                        external_conductivity_post.append(post)
                        external_conductivity_lambda.append(lambda_vector)

        # TODO: Add energy generation
        # TODO: Add convection

        # Create global pre, post and lambda
        # TODO: Add interaction matrix
        self.__pre = scipy.sparse.hstack(
            [scipy.sparse.block_diag(internal_conductivity_pre)] + external_conductivity_pre).tocsr()

        self.__post = scipy.sparse.hstack(
            [scipy.sparse.block_diag(internal_conductivity_post)] + external_conductivity_post).tocsr()

        self.__pi: scipy.sparse.csr_matrix = self.__pre.copy().transpose()

        self.__lambda_vector = numpy.concatenate(internal_conductivity_lambda + external_conductivity_lambda)
        self.__mo_index = mo_index
        self.__material_cubes_dict = material_cubes_dict

        self.__tcpn_simulator: TCPNSimulatorVariableStepEuler = TCPNSimulatorVariableStepEuler(self.__pre, self.__post,
                                                                                               self.__lambda_vector,
                                                                                               self.__pi, 64)

    @classmethod
    def obtain_places_in_touch_debug(cls, material_cube_a: SolidMaterialLocatedCube, material_cube_a_places_index: int,
                                     material_cube_b: SolidMaterialLocatedCube, material_cube_b_places_index: int) \
            -> List[Tuple[int, int]]:

        return cls.__obtain_places_in_touch(material_cube_a, material_cube_a_places_index, material_cube_b,
                                            material_cube_b_places_index)

    @classmethod
    def __obtain_places_in_touch(cls, material_cube_a: SolidMaterialLocatedCube, material_cube_a_places_index: int,
                                 material_cube_b: SolidMaterialLocatedCube, material_cube_b_places_index: int) \
            -> List[Tuple[int, int]]:
        # Touch in axis y
        if material_cube_a.location.y + material_cube_a.dimensions.y == material_cube_b.location.y:
            collision = cls.__check_rectangles_collision(
                (material_cube_a.location.x, material_cube_a.location.z),
                (material_cube_a.dimensions.x, material_cube_a.dimensions.z),
                (material_cube_b.location.x, material_cube_b.location.z),
                (material_cube_b.dimensions.x, material_cube_b.dimensions.z)
            )

            return [(material_cube_a_places_index + (z - material_cube_a.location.z) * material_cube_a.dimensions.x *
                     material_cube_a.dimensions.y + (
                             x - material_cube_a.location.x),
                     material_cube_b_places_index + (
                             z - material_cube_b.location.z) * material_cube_b.dimensions.x * material_cube_b.dimensions.y
                     + (material_cube_a.dimensions.y - 1) * material_cube_a.dimensions.x +
                     (x - material_cube_b.location.x)) for x, z in collision]

        elif material_cube_b.location.y + material_cube_b.dimensions.y == material_cube_a.location.y:
            collision = cls.__check_rectangles_collision(
                (material_cube_a.location.x, material_cube_a.location.z),
                (material_cube_a.dimensions.x, material_cube_a.dimensions.z),
                (material_cube_b.location.x, material_cube_b.location.z),
                (material_cube_b.dimensions.x, material_cube_b.dimensions.z)
            )

            return [(material_cube_a_places_index + (
                    z - material_cube_a.location.z) * material_cube_a.dimensions.x * material_cube_a.dimensions.y
                     + (material_cube_a.dimensions.y - 1) * material_cube_b.dimensions.x +
                     (x - material_cube_a.location.x),
                     material_cube_b_places_index + (z - material_cube_b.location.z) * material_cube_b.dimensions.x *
                     material_cube_b.dimensions.y +
                     (x - material_cube_b.location.x)) for x, z in collision]

        # Touch in axis x
        elif material_cube_a.location.x + material_cube_a.dimensions.x == material_cube_b.location.x:
            collision = cls.__check_rectangles_collision(
                (material_cube_a.location.y, material_cube_a.location.z),
                (material_cube_a.dimensions.y, material_cube_a.dimensions.z),
                (material_cube_b.location.y, material_cube_b.location.z),
                (material_cube_b.dimensions.y, material_cube_b.dimensions.z)
            )

            return [(material_cube_a_places_index + (
                    z - material_cube_a.location.z) * material_cube_a.dimensions.x * material_cube_a.dimensions.y +
                     (y - material_cube_a.location.y) * material_cube_a.dimensions.x + material_cube_b.dimensions.x - 1,
                     material_cube_b_places_index + (z - material_cube_b.location.z) *
                     material_cube_b.dimensions.x * material_cube_b.dimensions.y + (y - material_cube_b.location.y) *
                     material_cube_b.dimensions.x) for y, z in collision]

        elif material_cube_b.location.x + material_cube_b.dimensions.x == material_cube_a.location.x:
            collision = cls.__check_rectangles_collision(
                (material_cube_a.location.y, material_cube_a.location.z),
                (material_cube_a.dimensions.y, material_cube_a.dimensions.z),
                (material_cube_b.location.y, material_cube_b.location.z),
                (material_cube_b.dimensions.y, material_cube_b.dimensions.z)
            )

            return [(material_cube_a_places_index + (
                    z - material_cube_a.location.z) * material_cube_a.dimensions.x * material_cube_a.dimensions.y +
                     (y - material_cube_a.location.y) * material_cube_a.dimensions.x,
                     material_cube_b_places_index + (
                             z - material_cube_b.location.z) * material_cube_b.dimensions.x * material_cube_b.dimensions.y +
                     (y - material_cube_b.location.y) * material_cube_b.dimensions.x + material_cube_a.dimensions.x - 1)
                    for y, z in collision]

            # Touch in axis z
        elif material_cube_a.location.z + material_cube_a.dimensions.z == material_cube_b.location.z:
            collision = cls.__check_rectangles_collision(
                (material_cube_a.location.x, material_cube_a.location.y),
                (material_cube_a.dimensions.x, material_cube_a.dimensions.y),
                (material_cube_b.location.x, material_cube_b.location.y),
                (material_cube_b.dimensions.x, material_cube_b.dimensions.y)
            )

            return [(material_cube_a_places_index + (
                        material_cube_b.dimensions.z - 1) * material_cube_b.dimensions.x * material_cube_b.dimensions.y + (
                                 y - material_cube_a.location.y) * material_cube_a.dimensions.x + (
                             x - material_cube_a.location.x),
                     material_cube_b_places_index +
                     (y - material_cube_b.location.y) * material_cube_b.dimensions.x + material_cube_b.dimensions.x +
                     (x - material_cube_b.location.x)) for x, y in collision]

        elif material_cube_b.location.z + material_cube_b.dimensions.z == material_cube_a.location.z:
            collision = cls.__check_rectangles_collision(
                (material_cube_a.location.x, material_cube_a.location.y),
                (material_cube_a.dimensions.x, material_cube_a.dimensions.y),
                (material_cube_b.location.x, material_cube_b.location.y),
                (material_cube_b.dimensions.x, material_cube_b.dimensions.y)
            )

            return [(
                material_cube_a_places_index +
                (y - material_cube_a.location.y) * material_cube_a.dimensions.x + (x - material_cube_a.location.x),
                material_cube_b_places_index + (
                            material_cube_a.dimensions.z - 1) * material_cube_a.dimensions.x * material_cube_a.dimensions.y + (
                        y - material_cube_b.location.y) * material_cube_b.dimensions.x + material_cube_b.dimensions.x +
                (x - material_cube_b.location.x)) for x, y in collision]

        # No touch
        else:
            return []

    @staticmethod
    def __check_rectangles_collision(rectangle_a_position: Tuple[int, int], rectangle_a_dimensions: Tuple[int, int],
                                     rectangle_b_position: Tuple[int, int], rectangle_b_dimensions: Tuple[int, int]) \
            -> List[Tuple[int, int]]:
        """
        Calculate the collision between two rectangles
        """
        x0 = max(rectangle_a_position[0], rectangle_b_position[0])
        x1 = min(rectangle_a_position[0] + rectangle_a_dimensions[0],
                 rectangle_b_position[0] + rectangle_b_dimensions[0])

        y0 = max(rectangle_a_position[1], rectangle_b_position[1])
        y1 = min(rectangle_a_position[1] + rectangle_a_dimensions[1],
                 rectangle_b_position[1] + rectangle_b_dimensions[1])

        if x0 < x1 and y0 < y1:
            return [(i, j) for i in range(x0, x1) for j in range(y0, y1)]
        else:
            return []

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
        mo = actual_state.places_mo_vector
        mo_next = self.__tcpn_simulator.simulate_step(mo, amount_of_time)
        return CubedSpaceState(mo_next)

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


def obtain_min_temperature(heatmap_cube_list: List[TemperatureLocatedCube]) -> float:
    return min([i.temperatureMatrix.min() for i in heatmap_cube_list])


def obtain_max_temperature(heatmap_cube_list: List[TemperatureLocatedCube]) -> float:
    return max([i.temperatureMatrix.max() for i in heatmap_cube_list])
