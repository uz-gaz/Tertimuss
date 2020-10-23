import unittest

from cubed_space_thermal_simulator import UnitDimensions, UnitLocation, \
    CubedSpace, ThermalUnits, SolidMaterialLocatedCube, \
    obtain_min_temperature, obtain_max_temperature, plot_3d_heat_map_temperature, \
    InternalTemperatureBoosterLocatedCube, plot_2d_heat_map

from cubed_space_thermal_simulator.materials_pack import CooperSolidMaterial, SiliconSolidMaterial, \
    AirFreeEnvironmentProperties, AirForcedEnvironmentProperties
from cubed_space_thermal_simulator.physics_utils import create_energy_applicator


class CubedSpaceThermalSimulatorPlotTest(unittest.TestCase):
    def test_processor_heat_generation_plot(self):
        # Dimensions of the core
        core_dimensions = UnitDimensions(x=10, z=2, y=10)

        # Material of the core
        core_material = SiliconSolidMaterial()

        # Material of the board
        board_material = CooperSolidMaterial()

        # Core initial temperature
        # core_initial_temperature = 273.15 + 65
        core_0_initial_temperature = 273.15 + 25
        core_1_initial_temperature = 273.15 + 25
        core_2_initial_temperature = 273.15 + 25
        core_3_initial_temperature = 273.15 + 25

        # Board initial temperature
        board_initial_temperature = 273.15 + 25

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Min simulation value
        max_simulation_value = 273.15 + 40
        min_simulation_value = 273.15 + 20

        # Definition of the CPU shape and materials
        cpu_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=10, z=2, y=10),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            1: SolidMaterialLocatedCube(
                location=UnitLocation(x=30, z=2, y=10),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            2: SolidMaterialLocatedCube(
                location=UnitLocation(x=10, z=2, y=30),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            3: SolidMaterialLocatedCube(
                location=UnitLocation(x=30, z=2, y=30),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),

            # Board
            4: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=UnitDimensions(x=50, z=2, y=50),
                solidMaterial=board_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = AirFreeEnvironmentProperties()

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
            0: create_energy_applicator(SolidMaterialLocatedCube(
                location=UnitLocation(x=10, z=2, y=10),
                dimensions=core_dimensions,
                solidMaterial=board_material),
                watts_to_apply=20,
                cube_edge_size=cube_edge_size
            ),

            # Leakage power
            1: create_energy_applicator(SolidMaterialLocatedCube(
                location=UnitLocation(x=10, z=2, y=10),
                dimensions=core_dimensions,
                solidMaterial=board_material),
                watts_to_apply=leakage_alpha,
                cube_edge_size=cube_edge_size
            ),
            2: create_energy_applicator(SolidMaterialLocatedCube(
                location=UnitLocation(x=30, z=2, y=10),
                dimensions=core_dimensions,
                solidMaterial=board_material),
                watts_to_apply=leakage_alpha,
                cube_edge_size=cube_edge_size
            ),
            3: create_energy_applicator(SolidMaterialLocatedCube(
                location=UnitLocation(x=10, z=2, y=30),
                dimensions=core_dimensions,
                solidMaterial=board_material),
                watts_to_apply=leakage_alpha,
                cube_edge_size=cube_edge_size
            ),
            4: create_energy_applicator(SolidMaterialLocatedCube(
                location=UnitLocation(x=30, z=2, y=30),
                dimensions=core_dimensions,
                solidMaterial=board_material),
                watts_to_apply=leakage_alpha,
                cube_edge_size=cube_edge_size
            )
        }

        # Internal heat generators
        internal_heat_generators = {
            0: InternalTemperatureBoosterLocatedCube(
                location=UnitLocation(x=10, z=2, y=10),
                dimensions=core_dimensions,
                boostRateMultiplier=leakage_delta
            ),
            1: InternalTemperatureBoosterLocatedCube(
                location=UnitLocation(x=30, z=2, y=10),
                dimensions=core_dimensions,
                boostRateMultiplier=leakage_delta
            ),
            2: InternalTemperatureBoosterLocatedCube(
                location=UnitLocation(x=10, z=2, y=30),
                dimensions=core_dimensions,
                boostRateMultiplier=leakage_delta
            ),
            3: InternalTemperatureBoosterLocatedCube(
                location=UnitLocation(x=30, z=2, y=30),
                dimensions=core_dimensions,
                boostRateMultiplier=leakage_delta
            )
        }

        # Generate cubed space
        cubed_space = CubedSpace(
            material_cubes=cpu_definition,
            cube_edge_size=cube_edge_size,
            external_temperature_booster_points=external_heat_generators,
            internal_temperature_booster_points=internal_heat_generators,
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

        temperatures_vector = []

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        temperatures_vector.append(temperature_over_before_zero_seconds)

        # Apply energy over the cubed space
        number_of_iterations = 10
        for i in range(number_of_iterations):
            initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                     external_energy_application_points={0},  # {0, 1, 2, 3, 4},
                                                     # internal_energy_application_points={0, 1, 2, 3},
                                                     amount_of_time=0.5)
            temperature = cubed_space.obtain_temperature(actual_state=initial_state,
                                                         units=ThermalUnits.CELSIUS)

            temperatures_vector.append(temperature)

        for i, temperature in enumerate(temperatures_vector):
            # Zero seconds
            plot_3d_heat_map_temperature(temperature,
                                         min_temperature=min_simulation_value,
                                         max_temperature=max_simulation_value).show()

            plot_2d_heat_map(temperature_over_before_zero_seconds,
                             min_temperature=min_simulation_value,
                             max_temperature=max_simulation_value,
                             axis="Z", location_in_axis=1).show()

            min_temperature = obtain_min_temperature(temperature)
            max_temperature = obtain_max_temperature(temperature)

            print("Temperature before", i * 0.5, "seconds: min", min_temperature, ", max", max_temperature)

    def test_external_conduction_plot(self):
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
                location=UnitLocation(x=cubes_dimensions.x, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cube_1_material
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

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.1)
        temperature_over_before_point_one_seconds = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                                   units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.1)
        temperature_over_before_point_two_seconds = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                                   units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature(temperature_over_before_zero_seconds,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value).show()

        plot_2d_heat_map(temperature_over_before_zero_seconds,
                         min_temperature=min_simulation_value,
                         max_temperature=max_simulation_value, axis="Z", location_in_axis=2).show()

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature(temperature_over_before_point_one_seconds,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value).show()

        plot_2d_heat_map(temperature_over_before_point_one_seconds,
                         min_temperature=min_simulation_value,
                         max_temperature=max_simulation_value, axis="Z", location_in_axis=2).show()

        min_temperature = obtain_min_temperature(temperature_over_before_point_one_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_point_one_seconds)

        print("Temperature before 0.1 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature(temperature_over_before_point_two_seconds,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value).show()

        plot_2d_heat_map(temperature_over_before_point_two_seconds,
                         min_temperature=min_simulation_value,
                         max_temperature=max_simulation_value, axis="Z", location_in_axis=2).show()

        min_temperature = obtain_min_temperature(temperature_over_before_point_two_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_point_two_seconds)

        print("Temperature before 0.2 second: min", min_temperature, ", max", max_temperature)

    def test_internal_conduction_plot(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=2, z=2, y=2)

        # Cube 0 material
        cube_0_material = CooperSolidMaterial()

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
        environment_properties = AirForcedEnvironmentProperties()

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
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
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.9)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.9)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature(temperature_over_before_zero_seconds,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature(temperature_over_before_half_second,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature = obtain_max_temperature(temperature_over_before_half_second)

        print("Temperature before 0.5 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature(temperature_over_before_one_second,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature = obtain_max_temperature(temperature_over_before_one_second)

        print("Temperature before 1 second: min", min_temperature, ", max", max_temperature)


if __name__ == '__main__':
    unittest.main()
