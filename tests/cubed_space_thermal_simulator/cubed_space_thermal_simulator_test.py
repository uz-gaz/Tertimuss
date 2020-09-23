import unittest

from cubed_space_thermal_simulator import UnitDimensions, UnitLocation, \
    ExternalEnergyLocatedCube, InternalEnergyLocatedCube, CubedSpace, ThermalUnits, SolidMaterial, \
    FluidEnvironmentProperties, SolidMaterialLocatedCube, obtain_min_temperature, obtain_max_temperature, \
    plot_3d_heat_map_temperature_located_cube_list


class CubedSpaceThermalSimulatorTest(unittest.TestCase):
    @staticmethod
    def float_equal(value_1: float, value_2: float, error: float) -> bool:
        return value_2 - error <= value_1 <= value_2 + error

    def test_processor_heat_generation_plot(self):
        # Dimensions of the core
        core_dimensions = UnitDimensions(x=3, z=1, y=3)

        # Material of the core
        core_material = SolidMaterial(
            density=2330,
            specificHeatCapacities=712,
            thermalConductivity=148
        )

        # Material of the board
        board_material = SolidMaterial(
            density=8933,
            specificHeatCapacities=385,
            thermalConductivity=400
        )

        # Core initial temperature
        # core_initial_temperature = 273.15 + 65
        core_0_initial_temperature = 273.15 + 65
        core_1_initial_temperature = 273.15 + 25
        core_2_initial_temperature = 273.15 + 25
        core_3_initial_temperature = 273.15 + 25

        # Board initial temperature
        board_initial_temperature = 273.15 + 25

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Min simulation value
        min_simulation_value = board_initial_temperature - 10
        max_simulation_value = core_0_initial_temperature + 10

        # Definition of the CPU shape and materials
        cpu_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            1: SolidMaterialLocatedCube(
                location=UnitLocation(x=6, z=2, y=1),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            2: SolidMaterialLocatedCube(
                location=UnitLocation(x=1, z=2, y=6),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            3: SolidMaterialLocatedCube(
                location=UnitLocation(x=6, z=2, y=6),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),

            # Board
            4: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=UnitDimensions(x=10, z=2, y=10),
                solidMaterial=board_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FluidEnvironmentProperties(environmentConvectionFactor=0.001)

        # CPU energy consumption configuration
        #  Dynamic power = dynamic_alpha * F^3 + dynamic_beta
        #  Leakage power = current temperature * 2 * leakage_delta + leakage_alpha
        leakage_alpha: float = 0.001
        leakage_delta: float = 0.1
        dynamic_alpha: float = 1.52
        dynamic_beta: float = 0.08

        cpu_frequency: float = 1000

        # External heat generators
        external_heat_generators = {
            # Dynamic power
            0: ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                energy=dynamic_alpha * (cpu_frequency ** 3) + dynamic_beta,
                period=1
            ),

            # Leakage power
            1: ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            2: ExternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=1),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            3: ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=6),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            4: ExternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=6),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            )
        }

        # Internal heat generators
        internal_heat_generators = {
            0: InternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            1: InternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=1),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            2: InternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=6),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            3: InternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=6),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            )
        }

        # Generate cubed space
        cubed_space = CubedSpace(
            material_cubes=cpu_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points=external_heat_generators,
            fixed_internal_energy_application_points=internal_heat_generators,
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: core_0_initial_temperature,
                1: core_1_initial_temperature,
                2: core_2_initial_temperature,
                3: core_3_initial_temperature,
                4: board_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[0, 1, 2, 3, 4],
                                                 internal_energy_application_points=[0, 1, 2, 3], amount_of_time=0.5)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[0, 1, 2, 3, 4],
                                                 internal_energy_application_points=[0, 1, 2, 3], amount_of_time=0.5)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_zero_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_half_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature = obtain_max_temperature(temperature_over_before_half_second)

        print("Temperature before 0.5 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_one_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature = obtain_max_temperature(temperature_over_before_one_second)

        print("Temperature before 1 second: min", min_temperature, ", max", max_temperature)

    def test_external_conduction_plot(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=2, z=2, y=2)

        # Cube 0 material
        cube_0_material = SolidMaterial(
            density=2330,
            specificHeatCapacities=712,
            thermalConductivity=148
        )

        # Cube 1 material
        cube_1_material = SolidMaterial(
            density=8933,
            specificHeatCapacities=385,
            thermalConductivity=400
        )

        # Core initial temperature
        cube_0_initial_temperature = 273.15 + 65
        cube_1_initial_temperature = 273.15 + 25

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Min simulation value
        min_simulation_value = cube_1_initial_temperature - 10
        max_simulation_value = cube_0_initial_temperature + 10

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cube_0_material
            ),
            1: SolidMaterialLocatedCube(
                location=UnitLocation(x=2, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cube_1_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FluidEnvironmentProperties(environmentConvectionFactor=0.001)

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points={},
            fixed_internal_energy_application_points={},
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

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.01)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.1)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_zero_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_half_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature = obtain_max_temperature(temperature_over_before_half_second)

        print("Temperature before 0.5 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_one_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature = obtain_max_temperature(temperature_over_before_one_second)

        print("Temperature before 1 second: min", min_temperature, ", max", max_temperature)

    def test_internal_conduction_plot(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=20, z=20, y=20)

        # Cube 0 material
        cube_0_material = SolidMaterial(
            density=2330,
            specificHeatCapacities=712,
            thermalConductivity=148
        )

        # Core initial temperature
        cube_0_initial_temperature = 273.15 + 65

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Min simulation value
        min_simulation_value = cube_0_initial_temperature - 10
        max_simulation_value = cube_0_initial_temperature + 10

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cube_0_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FluidEnvironmentProperties(environmentConvectionFactor=0.001)

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points={},
            fixed_internal_energy_application_points={},
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: cube_0_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.9)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.9)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_zero_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_half_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature = obtain_max_temperature(temperature_over_before_half_second)

        print("Temperature before 0.5 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_one_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature = obtain_max_temperature(temperature_over_before_one_second)

        print("Temperature before 1 second: min", min_temperature, ", max", max_temperature)

    def test_internal_conduction_without_convection(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=3, z=3, y=3)

        # Cube material
        cuboid_material = SolidMaterial(
            density=2330,
            specificHeatCapacities=712,
            thermalConductivity=148
        )

        # Cuboid initial temperature
        cuboid_initial_temperature = 273.15 + 65

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cuboid_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points={},
            fixed_internal_energy_application_points={},
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
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.5)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.5)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

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
        cuboid_material = SolidMaterial(
            density=2330,
            specificHeatCapacities=712,
            thermalConductivity=148
        )

        # Core initial temperature
        cuboid_initial_temperature = 273.15 + 65

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cuboid_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FluidEnvironmentProperties(environmentConvectionFactor=0.001)

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points={},
            fixed_internal_energy_application_points={},
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
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.5)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.5)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

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

        assert (min_temperature_half <= min_temperature_one
                and max_temperature_half <= max_temperature_one)


if __name__ == '__main__':
    unittest.main()
