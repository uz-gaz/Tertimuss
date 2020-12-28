import unittest

from tertimuss.cubed_space_thermal_simulator import UnitDimensions, UnitLocation, CubedSpace, obtain_min_temperature, \
    obtain_max_temperature, LocatedCube

from tertimuss.cubed_space_thermal_simulator.materials_pack import CooperSolidMaterial, SiliconSolidMaterial, \
    AirForcedEnvironmentProperties


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

        assert (self.float_equal(min_temperature_half, cuboid_initial_temperature, error=0.5))
        assert (self.float_equal(max_temperature_half, cuboid_initial_temperature, error=0.5))
        assert (self.float_equal(min_temperature_one, cuboid_initial_temperature, error=0.5))
        assert (self.float_equal(max_temperature_one, cuboid_initial_temperature, error=0.5))

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

        # One second
        min_temperature_one = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature_one = obtain_max_temperature(temperature_over_before_one_second)

        assert (environment_temperature <= min_temperature_half <= cuboid_initial_temperature
                and max_temperature_half <= cuboid_initial_temperature)

        assert (environment_temperature <= min_temperature_one <= cuboid_initial_temperature
                and max_temperature_one <= cuboid_initial_temperature)

        assert (min_temperature_one <= min_temperature_half
                and max_temperature_one <= max_temperature_half)

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

        assert (environment_temperature <= min_temperature_one_second <= cube_0_initial_temperature and
                self.float_equal(min_temperature_one_second, max_temperature_one_second, 1))


if __name__ == '__main__':
    unittest.main()
