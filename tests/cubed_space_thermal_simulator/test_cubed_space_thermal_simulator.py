import unittest
from typing import Tuple, List

from tertimuss.cubed_space_thermal_simulator import UnitDimensions, UnitLocation, CubedSpace, obtain_min_temperature, \
    obtain_max_temperature, LocatedCube, InternalTemperatureBoosterLocatedCube

from tertimuss.cubed_space_thermal_simulator.materials_pack import CooperSolidMaterial, SiliconSolidMaterial, \
    AirForcedEnvironmentProperties, AirFreeEnvironmentProperties
from tertimuss.cubed_space_thermal_simulator.physics_utils import create_energy_applicator


class CubedSpaceThermalSimulatorTest(unittest.TestCase):
    @staticmethod
    def float_equal(value_1: float, value_2: float, error: float) -> bool:
        return value_2 - error <= value_1 <= value_2 + error

    def test_internal_conduction_without_convection(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=3, z=3, y=3)

        # Cube material
        cuboid_material = SiliconSolidMaterial()

        # Cuboid initial temperature
        cuboid_initial_temperature = 273.15 + 65

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: (cuboid_material,
                LocatedCube(
                    location=UnitLocation(x=0, z=0, y=0),
                    dimensions=cubes_dimensions)
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            environment_properties=None,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=cuboid_initial_temperature,
            material_cubes_temperatures={
                0: cuboid_initial_temperature
            },
            environment_temperature=None
        )
        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.5)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.5)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state)

        # Half second
        min_temperature_half = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature_half = obtain_max_temperature(temperature_over_before_half_second)

        # One second
        min_temperature_one = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature_one = obtain_max_temperature(temperature_over_before_one_second)

        assert (self.float_equal(min(min_temperature_half.values()), cuboid_initial_temperature, error=0.5))
        assert (self.float_equal(max(max_temperature_half.values()), cuboid_initial_temperature, error=0.5))
        assert (self.float_equal(min(min_temperature_one.values()), cuboid_initial_temperature, error=0.5))
        assert (self.float_equal(max(max_temperature_one.values()), cuboid_initial_temperature, error=0.5))

    def test_internal_conduction_with_convection(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=3, z=3, y=3)

        # Cube 0 material
        cuboid_material = SiliconSolidMaterial()

        # Core initial temperature
        cuboid_initial_temperature = 273.15 + 65

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: (cuboid_material,
                LocatedCube(
                    location=UnitLocation(x=0, z=0, y=0),
                    dimensions=cubes_dimensions)
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = AirForcedEnvironmentProperties()

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: cuboid_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.5)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.5)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state)

        # Half second
        min_temperature_half = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature_half = obtain_max_temperature(temperature_over_before_half_second)

        min_temperature_half = min(min_temperature_half.values())
        max_temperature_half = max(max_temperature_half.values())

        # One second
        min_temperature_one = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature_one = obtain_max_temperature(temperature_over_before_one_second)

        min_temperature_one = min(min_temperature_one.values())
        max_temperature_one = max(max_temperature_one.values())

        assert (environment_temperature <= min_temperature_half <= cuboid_initial_temperature
                and max_temperature_half <= cuboid_initial_temperature)

        assert (environment_temperature <= min_temperature_one <= cuboid_initial_temperature
                and max_temperature_one <= cuboid_initial_temperature)

        assert (min_temperature_one <= min_temperature_half
                and max_temperature_one <= max_temperature_half)

    def test_heat_conservation_simple(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=3, z=3, y=3)

        # Cube material
        cuboid_material = SiliconSolidMaterial()

        # Cuboid initial temperature
        system_initial_temperature = 273.15 + 45

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cube
            0: (cuboid_material,
                LocatedCube(
                    location=UnitLocation(x=0, z=0, y=0),
                    dimensions=cubes_dimensions)
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            environment_properties=None,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=system_initial_temperature,
            environment_temperature=None
        )

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.5)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.5)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state)

        # Half second
        min_temperature_half = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature_half = obtain_max_temperature(temperature_over_before_half_second)

        # One second
        min_temperature_one = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature_one = obtain_max_temperature(temperature_over_before_one_second)

        assert (self.float_equal(min(min_temperature_half.values()), system_initial_temperature, error=0.1))
        assert (self.float_equal(max(max_temperature_half.values()), system_initial_temperature, error=0.1))
        assert (self.float_equal(min(min_temperature_one.values()), system_initial_temperature, error=0.1))
        assert (self.float_equal(max(max_temperature_one.values()), system_initial_temperature, error=0.1))

    def test_external_conduction_with_convection(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=4, z=4, y=4)

        # Cube 0 material
        cube_0_material = SiliconSolidMaterial()

        # Cube 1 material
        cube_1_material = CooperSolidMaterial()

        # Core initial temperature
        cube_0_initial_temperature = 273.15 + 65
        cube_1_initial_temperature = 273.15 + 25

        # Board initial temperature
        environment_temperature = 273.15 + 15

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: (cube_0_material,
                LocatedCube(
                    location=UnitLocation(x=0, z=0, y=0),
                    dimensions=cubes_dimensions)
                ),
            1: (cube_1_material,
                LocatedCube(
                    location=UnitLocation(x=cubes_dimensions.x, z=0, y=0),
                    dimensions=cubes_dimensions)
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = AirForcedEnvironmentProperties()

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: cube_0_initial_temperature,
                1: cube_1_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=2)
        temperature_over_before_point_one_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        # Half second
        min_temperature_one_second = obtain_min_temperature(temperature_over_before_point_one_seconds)
        max_temperature_one_second = obtain_max_temperature(temperature_over_before_point_one_seconds)

        min_temperature_one_second = min(min_temperature_one_second.values())
        max_temperature_one_second = max(max_temperature_one_second.values())

        assert (environment_temperature <= min_temperature_one_second <= cube_0_initial_temperature and
                self.float_equal(min_temperature_one_second, max_temperature_one_second, 1))

    def test_processor_heat_conservation_processor(self):
        # Dimensions of the core
        core_dimensions = UnitDimensions(x=10, z=2, y=10)

        # Material of the core
        core_material = SiliconSolidMaterial()

        # Material of the board
        board_material = CooperSolidMaterial()

        # System initial temperature
        system_initial_temperature = 273.15 + 25

        # Core initial temperature
        core_initial_temperature = system_initial_temperature

        # Board initial temperature
        board_initial_temperature = system_initial_temperature

        # Environment initial temperature
        environment_temperature = system_initial_temperature

        # Definition of the CPU shape and materials
        cpu_definition = {
            # Cores
            0: (core_material,
                LocatedCube(
                    location=UnitLocation(x=10, z=2, y=10),
                    dimensions=core_dimensions)
                ),
            1: (core_material,
                LocatedCube(
                    location=UnitLocation(x=30, z=2, y=10),
                    dimensions=core_dimensions)
                ),
            2: (core_material,
                LocatedCube(
                    location=UnitLocation(x=10, z=2, y=30),
                    dimensions=core_dimensions)
                ),
            3: (core_material,
                LocatedCube(
                    location=UnitLocation(x=30, z=2, y=30),
                    dimensions=core_dimensions)
                ),

            # Board
            4: (board_material,
                LocatedCube(
                    location=UnitLocation(x=0, z=0, y=0),
                    dimensions=UnitDimensions(x=50, z=2, y=50))
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = AirFreeEnvironmentProperties()

        # Generate cubed space
        cubed_space = CubedSpace(
            material_cubes=cpu_definition,
            cube_edge_size=cube_edge_size,
            external_temperature_booster_points={},
            internal_temperature_booster_points={},
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: core_initial_temperature,
                1: core_initial_temperature,
                2: core_initial_temperature,
                3: core_initial_temperature,
                4: board_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        min_max_temperatures_vector: List[Tuple[float, float, float]] = [
            (0.0, core_initial_temperature, core_initial_temperature)]

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(actual_state=initial_state)
        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)
        min_max_temperatures_vector.append((0.0, min(min_temperature.values()), max(max_temperature.values())))

        # Apply energy over the cubed space
        number_of_iterations = 6
        for i in range(number_of_iterations):
            initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.5)
            temperature = cubed_space.obtain_temperature(actual_state=initial_state)
            min_temperature = obtain_min_temperature(temperature)
            max_temperature = obtain_max_temperature(temperature)
            min_max_temperatures_vector.append((0.0, min(min_temperature.values()), max(max_temperature.values())))

        assert all(i > system_initial_temperature - 0.1 for _, i, _ in min_max_temperatures_vector)
        assert all(i < system_initial_temperature + 0.1 for _, _, i in min_max_temperatures_vector)


if __name__ == '__main__':
    unittest.main()
