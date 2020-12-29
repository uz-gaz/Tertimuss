import itertools
from typing import List, Optional, Tuple, Set, Literal

import scipy.sparse

from tertimuss.tcpn_simulator import TCPNSimulatorVariableStepRK, AbstractTCPNSimulatorVariableStep, \
    TCPNSimulatorVariableStepEuler
from ._basic_types import *


class CubedSpaceState(object):
    def __init__(self, places_mo_vector: numpy.ndarray):
        self.places_mo_vector = places_mo_vector


class CubedSpace(object):
    def __init__(self, material_cubes: Dict[int, Tuple[SolidMaterial, LocatedCube]], cube_edge_size: float,
                 environment_properties: Optional[FluidEnvironmentProperties] = None,
                 external_temperature_booster_points: Optional[Dict[int, ExternalTemperatureBoosterLocatedCube]] = None,
                 internal_temperature_booster_points: Optional[Dict[int, InternalTemperatureBoosterLocatedCube]] = None,
                 simulation_precision: Literal["LOW", "MIDDLE", "HIGH"] = "HIGH"):
        """
        This function create a cubedSpace

        :param material_cubes: List of cubes that conform the space. Each cube will have defined it's dimensions in unit
         units, the position in units and the thermal properties of the cube. Its assumed that all material cubes are
         metals
        :param cube_edge_size: Cubes' edge size in m (each cube will have the same edge size).
        :param environment_properties: The material that will be surrounded the cube will have these properties.
         This material won't change him temperature, however it will affect to the mesh temperature.
        :param external_temperature_booster_points: This parameter is only used with optimization purposes. If is
         not null, all of the elements of external_energy_application_points in the function apply_energy, must be in
         fixed_external_energy_application_points.
        :param internal_temperature_booster_points: This parameter is only used with optimization purposes. If is
         not null, all of the elements of internal_energy_application_points in the function apply_energy, must be in
         fixed_internal_energy_application_points.
        """
        # Fill fields if are empty
        external_temperature_booster_points = external_temperature_booster_points \
            if external_temperature_booster_points is not None else dict()
        internal_temperature_booster_points = internal_temperature_booster_points \
            if internal_temperature_booster_points is not None else dict()

        # Different precision types
        # LOW: Euler and float32
        # MIDDLE: RK and float32
        # HIGH: RK and float64

        # Select precision type
        if simulation_precision == "LOW":
            dtype = numpy.float32
        elif simulation_precision == "MIDDLE":
            dtype = numpy.float32
        elif simulation_precision == "HIGH":
            dtype = numpy.float64
        else:
            raise Exception("Not available precision")

        # Incidence matrix petri net structure
        # +------------+------------+-----------------+----+-------+
        # |            |            |                 |    |       |
        # | Internal   | External   | Convection      |    |       |
        # | cuboids    | cuboids    | heat extraction |    |       |
        # | conduction | conduction | to environment  |    |       |
        # |            |            |                 |    |       |
        # +------------+------------+-----------------+    |       |
        # |                                                |       |
        # |Convection heat acquirement from environment    |       |
        # |                                                |       |
        # +------------------------------------------------+       |
        # |                                                        |
        # |Heat generation                                         |
        # |                                                        |
        # +--------------------------------------------------------+

        # TCPN definition
        mo_index = {}
        material_cubes_dict = {}
        internal_conductivity_pre = []
        internal_conductivity_post = []
        internal_conductivity_lambda = []
        mo_cubes_size = []
        places_material_mapping = []
        location_places_mapping: Dict[Tuple[int, int, int], int] = {}

        # First create internal conductivity for each material cube
        for material_cube_index, material_cube in material_cubes.items():
            # Parameters
            x: int = material_cube[1].dimensions.x
            y: int = material_cube[1].dimensions.y
            z: int = material_cube[1].dimensions.z

            rho: float = material_cube[0].density
            k: float = material_cube[0].thermalConductivity
            cp: float = material_cube[0].specificHeatCapacity

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
            pre = scipy.sparse.lil_matrix((p, t), dtype=dtype)
            post = scipy.sparse.lil_matrix((p, t), dtype=dtype)

            # All lambdas are equals
            lambda_vector = numpy.full(t, lambda_side, dtype=dtype)

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
            places_material_mapping[mo_index[material_cube_index]:
                                    mo_index[material_cube_index] +
                                    material_cube[1].dimensions.x *
                                    material_cube[1].dimensions.y *
                                    material_cube[1].dimensions.z] = (material_cube[1].dimensions.x *
                                                                      material_cube[1].dimensions.y *
                                                                      material_cube[1].dimensions.z) * [
                                                                         material_cube_index]

            # Fill location to place mapping dict
            for actual_z in range(z):
                for actual_y in range(y):
                    for actual_x in range(x):
                        local_place = actual_z * y * x + actual_y * x + actual_x
                        global_place = mo_index[material_cube_index] + local_place
                        location_places_mapping[(material_cube[1].location.x + actual_x,
                                                 material_cube[1].location.y + actual_y,
                                                 material_cube[1].location.z + actual_z)] = global_place

        # Add interaction between cuboids
        mo_places_size = sum(mo_cubes_size)

        external_conductivity_pre = []
        external_conductivity_post = []
        external_conductivity_lambda = []

        # Places that touch other place
        places_with_contact: Set[int] = set()

        for material_cube_a_index, material_cube_a in material_cubes.items():
            for material_cube_b_index, material_cube_b in material_cubes.items():
                # Avoid duplicities
                if material_cube_a_index < material_cube_b_index:
                    places_in_touch = self.__obtain_places_in_touch(material_cube_a, mo_index[material_cube_a_index],
                                                                    material_cube_b, mo_index[material_cube_b_index])
                    for place_a, place_b in places_in_touch:
                        pre = scipy.sparse.lil_matrix((mo_places_size, 2), dtype=dtype)
                        post = scipy.sparse.lil_matrix((mo_places_size, 2), dtype=dtype)

                        # Transition 1, from A -> B
                        pre[place_a, 0] = 1
                        post[place_b, 0] = (material_cube_a[0].density
                                            * material_cube_a[0].specificHeatCapacity) / \
                                           (material_cube_b[0].density
                                            * material_cube_b[0].specificHeatCapacity)

                        # Transition 2, from B -> A
                        pre[place_b, 1] = 1
                        post[place_a, 1] = (material_cube_b[0].density
                                            * material_cube_b[0].specificHeatCapacity) / \
                                           (material_cube_a[0].density
                                            * material_cube_a[0].specificHeatCapacity)

                        # All lambdas are equals
                        lambda_vector = numpy.zeros(shape=2, dtype=dtype)

                        # Calculate lambda from A -> B
                        lambda_vector[0] = (material_cube_a[0].thermalConductivity
                                            * material_cube_b[0].thermalConductivity) / \
                                           (material_cube_a[0].density
                                            * material_cube_a[0].specificHeatCapacity
                                            * (material_cube_a[0].thermalConductivity
                                               + material_cube_b[0].thermalConductivity)
                                            * (cube_edge_size ** 2))

                        # Calculate lambda from B -> A
                        lambda_vector[1] = (material_cube_a[0].thermalConductivity
                                            * material_cube_b[0].thermalConductivity) / \
                                           (material_cube_b[0].density
                                            * material_cube_b[0].specificHeatCapacity
                                            * (material_cube_a[0].thermalConductivity
                                               + material_cube_b[0].thermalConductivity)
                                            * (cube_edge_size ** 2))

                        # Append to global values
                        external_conductivity_pre.append(pre)
                        external_conductivity_post.append(post)
                        external_conductivity_lambda.append(lambda_vector)

                        # Add booth places to the set of places in contact
                        places_with_contact.add(place_a)
                        places_with_contact.add(place_b)

        # Add convection
        places_with_convection: Set[int] = set(range(mo_places_size)).difference(
            places_with_contact) if environment_properties is not None else set()

        # Return the convection lambda of a material
        def _convection_lambda_of_material(_material_cube: Tuple[SolidMaterial, LocatedCube]) -> float:
            return environment_properties.heatTransferCoefficient / (
                    cube_edge_size * _material_cube[0].density *
                    _material_cube[0].specificHeatCapacity)

        # This data structure store for each place in contact with the environment the heat extraction transition'
        # lambda value
        conv_lambda_by_place: List[Tuple[int, float]] = [
            (i, _convection_lambda_of_material(material_cubes[places_material_mapping[i]])) for i in
            places_with_convection]

        # This data structure store for each material the places that have this material and are in contact
        # with the environment and the associated lambda
        conv_lambda_shared_material_places: List[Tuple[float, List[int]]] = [(k, [j[0] for j in i]) for k, i in
                                                                             itertools.groupby(conv_lambda_by_place,
                                                                                               key=lambda j: j[1])]

        # Heat extracted to the air
        pre_conv_1 = scipy.sparse.lil_matrix((mo_places_size, len(places_with_convection)), dtype=dtype)
        post_conv_1 = scipy.sparse.lil_matrix((mo_places_size, len(places_with_convection)), dtype=dtype)
        lambda_vector_conv_1 = numpy.zeros(len(places_with_convection), dtype=dtype)

        for transition_index, (place, transition_lambda) in enumerate(conv_lambda_by_place):
            pre_conv_1[place, transition_index] = 1
            lambda_vector_conv_1[transition_index] = transition_lambda

        # Heat acquired from the air
        pre_conv_2 = scipy.sparse.lil_matrix(
            (mo_places_size + len(conv_lambda_shared_material_places), len(conv_lambda_shared_material_places)),
            dtype=dtype)
        post_conv_2 = scipy.sparse.lil_matrix(
            (mo_places_size + len(conv_lambda_shared_material_places), len(conv_lambda_shared_material_places)),
            dtype=dtype)
        lambda_vector_conv_2 = numpy.zeros(len(conv_lambda_shared_material_places), dtype=dtype)

        for transition_index, (material_lambda, places) in enumerate(conv_lambda_shared_material_places):
            lambda_vector_conv_2[transition_index] = material_lambda
            pre_conv_2[mo_places_size + transition_index, transition_index] = 1
            post_conv_2[mo_places_size + transition_index, transition_index] = 1
            for place in places:
                post_conv_2[place, transition_index] = 1

        # Internal temperature boost
        # Store for each internal temperature boost, the first transition index and the number of transitions related
        internal_temperature_boost_transitions: Dict[int, Tuple[int, int]] = {}
        pre_internal_gen = []
        post_internal_gen = []
        lambda_vector_internal_gen = []

        for internal_temperature_booster_point_index, internal_temperature_booster_point in \
                internal_temperature_booster_points.items():
            places = []
            for actual_z in range(internal_temperature_booster_point.dimensions.z):
                for actual_y in range(internal_temperature_booster_point.dimensions.y):
                    for actual_x in range(internal_temperature_booster_point.dimensions.x):
                        global_z = actual_z + internal_temperature_booster_point.location.z
                        global_y = actual_y + internal_temperature_booster_point.location.y
                        global_x = actual_x + internal_temperature_booster_point.location.x

                        if location_places_mapping.__contains__((global_x, global_y, global_z)):
                            places.append(location_places_mapping[(global_x, global_y, global_z)])

            pre = scipy.sparse.lil_matrix((pre_conv_2.shape[0], len(places)), dtype=dtype)
            post = scipy.sparse.lil_matrix((post_conv_2.shape[0], len(places)), dtype=dtype)
            lambda_vector = numpy.zeros(len(places))

            for place_index, place in enumerate(places):
                pre[place, place_index] = 1
                post[place, place_index] = 2
                lambda_vector[place_index] = internal_temperature_booster_point.boostRateMultiplier

            # Store matrix
            internal_temperature_boost_transition_start = sum(
                [i[1] for _, i in internal_temperature_boost_transitions.items()])

            internal_temperature_boost_transitions[internal_temperature_booster_point_index] = \
                (internal_temperature_boost_transition_start, len(places))

            pre_internal_gen.append(pre)
            post_internal_gen.append(post)
            lambda_vector_internal_gen.append(lambda_vector)

        # External temperature boost
        external_temperature_boost_places: Dict[int, int] = {}
        pre_external_gen_1 = scipy.sparse.lil_matrix((post_conv_2.shape[0], len(external_temperature_booster_points)),
                                                     dtype=dtype)
        post_external_gen_1 = scipy.sparse.lil_matrix((post_conv_2.shape[0], len(external_temperature_booster_points)),
                                                      dtype=dtype)
        lambda_vector_external_gen = numpy.zeros(len(external_temperature_booster_points), dtype=dtype)

        for transition_index, (external_temperature_booster_point_index, external_temperature_booster_point) in \
                enumerate(external_temperature_booster_points.items()):
            places = []
            for actual_z in range(external_temperature_booster_point.dimensions.z):
                for actual_y in range(external_temperature_booster_point.dimensions.y):
                    for actual_x in range(external_temperature_booster_point.dimensions.x):
                        global_z = actual_z + external_temperature_booster_point.location.z
                        global_y = actual_y + external_temperature_booster_point.location.y
                        global_x = actual_x + external_temperature_booster_point.location.x

                        if location_places_mapping.__contains__((global_x, global_y, global_z)):
                            places.append(location_places_mapping[(global_x, global_y, global_z)])

            for place_index, place in enumerate(places):
                post_external_gen_1[place, transition_index] = 1

            lambda_vector_external_gen[transition_index] = external_temperature_booster_point.boostRate

            external_temperature_boost_places[external_temperature_booster_point_index] = len(
                external_temperature_boost_places)

        # Create global pre, post and lambda
        # Add interaction matrix
        pre = scipy.sparse.hstack(
            [scipy.sparse.block_diag(internal_conductivity_pre)] + external_conductivity_pre + [pre_conv_1])
        pre = scipy.sparse.vstack(
            [pre, scipy.sparse.lil_matrix((len(conv_lambda_shared_material_places), pre.shape[1]), dtype=dtype)])
        pre = scipy.sparse.hstack([pre, pre_conv_2])
        pre = scipy.sparse.hstack([pre] + pre_internal_gen)
        pre = scipy.sparse.vstack(
            [pre, scipy.sparse.lil_matrix((len(external_temperature_booster_points), pre.shape[1]), dtype=dtype)])
        pre = scipy.sparse.hstack(
            [pre, scipy.sparse.vstack([pre_external_gen_1, scipy.sparse.eye(len(external_temperature_booster_points))])]
        )
        self.__pre = pre.tocsr()

        post = scipy.sparse.hstack(
            [scipy.sparse.block_diag(internal_conductivity_post)] + external_conductivity_post + [post_conv_1])
        post = scipy.sparse.vstack(
            [post, scipy.sparse.lil_matrix((len(conv_lambda_shared_material_places), post.shape[1]), dtype=dtype)])
        post = scipy.sparse.hstack([post, post_conv_2])
        post = scipy.sparse.hstack([post] + post_internal_gen)
        post = scipy.sparse.vstack(
            [post, scipy.sparse.lil_matrix((len(external_temperature_booster_points), post.shape[1]), dtype=dtype)])
        post = scipy.sparse.hstack(
            [post,
             scipy.sparse.vstack([post_external_gen_1, scipy.sparse.eye(len(external_temperature_booster_points))])]
        )
        self.__post = post.tocsr()

        self.__pi: scipy.sparse.csr_matrix = self.__pre.copy().transpose()

        self.__lambda_vector = numpy.concatenate(
            internal_conductivity_lambda + external_conductivity_lambda + [lambda_vector_conv_1, lambda_vector_conv_2]
            + lambda_vector_internal_gen + [lambda_vector_external_gen])

        self.__mo_index = mo_index
        self.__material_cubes_dict = material_cubes_dict

        self.__environment_number_of_places = len(conv_lambda_shared_material_places)

        self.__simulation_precision = dtype

        if simulation_precision == "HIGH" or simulation_precision == "MIDDLE":
            self.__tcpn_simulator: AbstractTCPNSimulatorVariableStep = TCPNSimulatorVariableStepRK(
                self.__pre,
                self.__post,
                self.__lambda_vector,
                self.__pi
            )
        elif simulation_precision == "LOW":
            self.__tcpn_simulator: AbstractTCPNSimulatorVariableStep = TCPNSimulatorVariableStepEuler(
                self.__pre, self.__post,
                self.__lambda_vector,
                self.__pi, 128, True
            )
        else:
            raise Exception("Not available precision")

        self.__internal_temperature_boost_transitions: Dict[
            int, Tuple[int, int]] = internal_temperature_boost_transitions

        self.__external_temperature_boost_places = external_temperature_boost_places

        self.__activated_internal_temperature_boost_transitions: Set[int] = \
            {i for i, _ in internal_temperature_booster_points.items()}
        self.__activated_external_temperature_boost_transitions: Set[int] = \
            {i for i, _ in external_temperature_booster_points.items()}

    @classmethod
    def __obtain_places_in_touch(cls, material_cube_a: Tuple[SolidMaterial, LocatedCube],
                                 material_cube_a_places_index: int,
                                 material_cube_b: Tuple[SolidMaterial, LocatedCube], material_cube_b_places_index: int) \
            -> List[Tuple[int, int]]:
        # Touch in axis y
        if material_cube_a[1].location.y + material_cube_a[1].dimensions.y == material_cube_b[1].location.y:
            collision = cls.__check_rectangles_collision(
                (material_cube_a[1].location.x, material_cube_a[1].location.z),
                (material_cube_a[1].dimensions.x, material_cube_a[1].dimensions.z),
                (material_cube_b[1].location.x, material_cube_b[1].location.z),
                (material_cube_b[1].dimensions.x, material_cube_b[1].dimensions.z)
            )

            return [
                (material_cube_a_places_index + (z - material_cube_a[1].location.z) * material_cube_a[1].dimensions.x *
                 material_cube_a[1].dimensions.y + (
                         x - material_cube_a[1].location.x),
                 material_cube_b_places_index + (
                         z - material_cube_b[1].location.z) * material_cube_b[1].dimensions.x
                 * material_cube_b[1].dimensions.y + (material_cube_a[1].dimensions.y - 1)
                 * material_cube_a[1].dimensions.x + (x - material_cube_b[1].location.x)) for x, z in collision]

        elif material_cube_b[1].location.y + material_cube_b[1].dimensions.y == material_cube_a[1].location.y:
            collision = cls.__check_rectangles_collision(
                (material_cube_a[1].location.x, material_cube_a[1].location.z),
                (material_cube_a[1].dimensions.x, material_cube_a[1].dimensions.z),
                (material_cube_b[1].location.x, material_cube_b[1].location.z),
                (material_cube_b[1].dimensions.x, material_cube_b[1].dimensions.z)
            )

            return [(material_cube_a_places_index + (
                    z - material_cube_a[1].location.z) * material_cube_a[1].dimensions.x * material_cube_a[
                         1].dimensions.y
                     + (material_cube_a[1].dimensions.y - 1) * material_cube_b[1].dimensions.x +
                     (x - material_cube_a[1].location.x),
                     material_cube_b_places_index + (z - material_cube_b[1].location.z) * material_cube_b[
                         1].dimensions.x *
                     material_cube_b[1].dimensions.y +
                     (x - material_cube_b[1].location.x)) for x, z in collision]

        # Touch in axis x
        elif material_cube_a[1].location.x + material_cube_a[1].dimensions.x == material_cube_b[1].location.x:
            collision = cls.__check_rectangles_collision(
                (material_cube_a[1].location.y, material_cube_a[1].location.z),
                (material_cube_a[1].dimensions.y, material_cube_a[1].dimensions.z),
                (material_cube_b[1].location.y, material_cube_b[1].location.z),
                (material_cube_b[1].dimensions.y, material_cube_b[1].dimensions.z)
            )

            return [(material_cube_a_places_index + (
                    z - material_cube_a[1].location.z) * material_cube_a[1].dimensions.x * material_cube_a[
                         1].dimensions.y +
                     (y - material_cube_a[1].location.y) * material_cube_a[1].dimensions.x + material_cube_b[
                         1].dimensions.x - 1,
                     material_cube_b_places_index + (z - material_cube_b[1].location.z) *
                     material_cube_b[1].dimensions.x * material_cube_b[1].dimensions.y + (
                             y - material_cube_b[1].location.y) *
                     material_cube_b[1].dimensions.x) for y, z in collision]

        elif material_cube_b[1].location.x + material_cube_b[1].dimensions.x == material_cube_a[1].location.x:
            collision = cls.__check_rectangles_collision(
                (material_cube_a[1].location.y, material_cube_a[1].location.z),
                (material_cube_a[1].dimensions.y, material_cube_a[1].dimensions.z),
                (material_cube_b[1].location.y, material_cube_b[1].location.z),
                (material_cube_b[1].dimensions.y, material_cube_b[1].dimensions.z)
            )

            return [(material_cube_a_places_index + (
                    z - material_cube_a[1].location.z) * material_cube_a[1].dimensions.x * material_cube_a[
                         1].dimensions.y +
                     (y - material_cube_a[1].location.y) * material_cube_a[1].dimensions.x,
                     material_cube_b_places_index + (
                             z - material_cube_b[1].location.z) * material_cube_b[1].dimensions.x * material_cube_b[
                         1].dimensions.y +
                     (y - material_cube_b[1].location.y) * material_cube_b[1].dimensions.x + material_cube_a[
                         1].dimensions.x - 1)
                    for y, z in collision]

            # Touch in axis z
        elif material_cube_a[1].location.z + material_cube_a[1].dimensions.z == material_cube_b[1].location.z:
            collision = cls.__check_rectangles_collision(
                (material_cube_a[1].location.x, material_cube_a[1].location.y),
                (material_cube_a[1].dimensions.x, material_cube_a[1].dimensions.y),
                (material_cube_b[1].location.x, material_cube_b[1].location.y),
                (material_cube_b[1].dimensions.x, material_cube_b[1].dimensions.y)
            )

            return [(material_cube_a_places_index + (
                    material_cube_b[1].dimensions.z - 1) * material_cube_b[1].dimensions.x * material_cube_b[
                         1].dimensions.y + (
                             y - material_cube_a[1].location.y) * material_cube_a[1].dimensions.x + (
                             x - material_cube_a[1].location.x),
                     material_cube_b_places_index +
                     (y - material_cube_b[1].location.y) * material_cube_b[1].dimensions.x + material_cube_b[
                         1].dimensions.x +
                     (x - material_cube_b[1].location.x)) for x, y in collision]

        elif material_cube_b[1].location.z + material_cube_b[1].dimensions.z == material_cube_a[1].location.z:
            collision = cls.__check_rectangles_collision(
                (material_cube_a[1].location.x, material_cube_a[1].location.y),
                (material_cube_a[1].dimensions.x, material_cube_a[1].dimensions.y),
                (material_cube_b[1].location.x, material_cube_b[1].location.y),
                (material_cube_b[1].dimensions.x, material_cube_b[1].dimensions.y)
            )

            return [(
                material_cube_a_places_index +
                (y - material_cube_a[1].location.y) * material_cube_a[1].dimensions.x + (
                        x - material_cube_a[1].location.x),
                material_cube_b_places_index + (
                        material_cube_a[1].dimensions.z - 1) * material_cube_a[1].dimensions.x * material_cube_a[
                    1].dimensions.y + (
                        y - material_cube_b[1].location.y) * material_cube_b[1].dimensions.x + material_cube_b[
                    1].dimensions.x +
                (x - material_cube_b[1].location.x)) for x, y in collision]

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

    def apply_energy(self, actual_state: CubedSpaceState, amount_of_time: float,
                     external_energy_application_points: Optional[Set[int]] = None,
                     internal_energy_application_points: Optional[Set[int]] = None) -> CubedSpaceState:
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
        # Fill fields if null
        external_energy_application_points = external_energy_application_points \
            if external_energy_application_points is not None else set()
        internal_energy_application_points = internal_energy_application_points \
            if internal_energy_application_points is not None else set()

        mo = actual_state.places_mo_vector

        if self.__activated_external_temperature_boost_transitions != external_energy_application_points:
            # Modify control for external points
            number_of_external_temperature_boost_places = len(self.__external_temperature_boost_places)
            self.__activated_external_temperature_boost_transitions = external_energy_application_points
            control = numpy.zeros(number_of_external_temperature_boost_places)
            for i in external_energy_application_points:
                if self.__external_temperature_boost_places.__contains__(i):
                    control[self.__external_temperature_boost_places[i]] = 1.0
            mo[-number_of_external_temperature_boost_places:] = control

        if self.__activated_internal_temperature_boost_transitions != internal_energy_application_points:
            # Modify control for internal points
            number_of_external_temperature_boost_places = len(self.__external_temperature_boost_places)
            number_of_internal_temperature_boost_places = sum(
                [i for _, (_, i) in self.__internal_temperature_boost_transitions.items()])
            self.__activated_internal_temperature_boost_transitions = internal_energy_application_points
            control = numpy.zeros(number_of_internal_temperature_boost_places)
            for i in internal_energy_application_points:
                if self.__internal_temperature_boost_transitions.__contains__(i):
                    (start_transition, number_of_transitions) = self.__internal_temperature_boost_transitions[i]
                    control[start_transition: start_transition + number_of_transitions] = 1.0
            self.__tcpn_simulator.set_control(
                numpy.concatenate(
                    [numpy.ones(self.__pre.shape[1] - len(control) - number_of_external_temperature_boost_places),
                     control, numpy.ones(number_of_external_temperature_boost_places)]))

        mo_next = self.__tcpn_simulator.simulate_step(mo, amount_of_time)
        return CubedSpaceState(mo_next)

    def obtain_temperature(self, actual_state: CubedSpaceState) -> Dict[int, TemperatureLocatedCube]:
        """
        This function return the temperature in each cube of unit edge that conform the cubedSpace

        :param actual_state:
        :return: List of temperature blocks in kelvin
        """
        temperature_cubes = {}

        for i, v in self.__mo_index.items():
            material_cube = self.__material_cubes_dict[i]
            number_of_occupied_places = material_cube[1].dimensions.x * material_cube[1].dimensions.y * material_cube[
                1].dimensions.z
            temperature_places = actual_state.places_mo_vector[v: v + number_of_occupied_places]
            temperature_cubes[i] = TemperatureLocatedCube(material_cube[1].dimensions, material_cube[1].location,
                                                          temperature_places)

        return temperature_cubes

    def create_initial_state(self, default_temperature: float,
                             material_cubes_temperatures: Optional[Dict[int, float]] = None,
                             environment_temperature: Optional[float] = None) -> CubedSpaceState:
        """

        :param default_temperature:
        :param material_cubes_temperatures: List of [material cube id, material cube temperature (Kelvin)]
        :param environment_temperature: Environment temperature (Kelvin)
        :return:
        """
        places_temperature = []
        for i, v in self.__mo_index.items():
            material_cube = self.__material_cubes_dict[i]
            number_of_occupied_places = material_cube[1].dimensions.x * material_cube[1].dimensions.y * material_cube[
                1].dimensions.z
            local_places_temperature = numpy.ones(shape=(number_of_occupied_places), dtype=self.__simulation_precision)

            if material_cubes_temperatures is not None and material_cubes_temperatures.__contains__(i):
                places_temperature.append(local_places_temperature * material_cubes_temperatures[i])
            else:
                places_temperature.append(local_places_temperature * default_temperature)

        # Set environment temperature value
        environment_temperature = environment_temperature if environment_temperature is not None \
            else default_temperature

        # Append environment temperature
        if self.__environment_number_of_places != 0:
            places_temperature.append(environment_temperature * numpy.ones(shape=(self.__environment_number_of_places),
                                                                           dtype=self.__simulation_precision))

        return CubedSpaceState(
            numpy.concatenate(places_temperature + [numpy.ones(len(self.__external_temperature_boost_places))]))


def obtain_min_temperature(heatmap_cube_list: Dict[int, TemperatureLocatedCube]) -> Dict[int, float]:
    return {i: j.temperatureMatrix.min() for i, j in heatmap_cube_list.items()}


def obtain_max_temperature(heatmap_cube_list: Dict[int, TemperatureLocatedCube]) -> Dict[int, float]:
    return {i: j.temperatureMatrix.max() for i, j in heatmap_cube_list.items()}
