import unittest
from typing import Dict

from matplotlib import animation

from tertimuss.cubed_space_thermal_simulator import Dimensions, Location, \
    Model, obtain_min_temperature, obtain_max_temperature, plot_3d_heat_map_temperature, \
    plot_2d_heat_map, generate_video_2d_heat_map, generate_video_3d_heat_map, \
    Cuboid, TMInternal, PhysicalCuboid

from tertimuss.cubed_space_thermal_simulator.materials_pack import SMCooper, SMSilicon, \
    FEAirFree, FEAirForced
from tertimuss.cubed_space_thermal_simulator.physics_utils import create_energy_applicator


class CubedSpaceThermalSimulatorPlotTest(unittest.TestCase):
    @unittest.skip("Manual visualization test")
    def test_processor_heat_generation_plot(self):
        # Dimensions of the core
        core_dimensions = Dimensions(x=10, z=2, y=10)

        # Material of the core
        core_material = SMSilicon()

        # Material of the board
        board_material = SMCooper()

        # Core initial temperature
        # core_initial_temperature = 273.15 + 65
        core_0_initial_temperature = 273.15 + 25
        core_1_initial_temperature = 273.15 + 25
        core_2_initial_temperature = 273.15 + 25
        core_3_initial_temperature = 273.15 + 25

        # Board initial temperature
        board_initial_temperature = 273.15 + 25

        # Environment initial temperature
        environment_temperature = 273.15 + 25

        # Min simulation value
        max_simulation_value = 273.15 + 80
        min_simulation_value = 273.15 + 20

        # Definition of the CPU shape and materials
        cpu_definition = {
            # Cores
            0: (core_material,
                Cuboid(
                    location=Location(x=10, z=2, y=10),
                    dimensions=core_dimensions)
                ),
            1: (core_material,
                Cuboid(
                    location=Location(x=30, z=2, y=10),
                    dimensions=core_dimensions)
                ),
            2: (core_material,
                Cuboid(
                    location=Location(x=10, z=2, y=30),
                    dimensions=core_dimensions)
                ),
            3: (core_material,
                Cuboid(
                    location=Location(x=30, z=2, y=30),
                    dimensions=core_dimensions)
                ),

            # Board
            4: (board_material,
                Cuboid(
                    location=Location(x=0, z=0, y=0),
                    dimensions=Dimensions(x=50, z=2, y=50))
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FEAirFree()

        # CPU energy consumption configuration
        #  Dynamic power = dynamic_alpha * F^3 + dynamic_beta
        #  Leakage power = current temperature * 2 * leakage_delta + leakage_alpha
        leakage_alpha: float = 0.001
        leakage_delta: float = 0.1
        dynamic_alpha: float = 19 * 1000 ** -3
        dynamic_beta: float = 2

        cpu_frequency: float = 1000

        watts_to_apply = dynamic_alpha * (cpu_frequency ** 3) + dynamic_beta

        # External heat generators
        external_heat_generators = {
            # Dynamic power
            0: create_energy_applicator((core_material,
                                         Cuboid(
                                             location=Location(x=10, z=2, y=10),
                                             dimensions=core_dimensions)
                                         ),
                                        watts_to_apply=watts_to_apply,
                                        cube_edge_size=cube_edge_size
                                        ),

            # Leakage power
            1: create_energy_applicator((core_material,
                                         Cuboid(
                                             location=Location(x=10, z=2, y=10),
                                             dimensions=core_dimensions)
                                         ),
                                        watts_to_apply=leakage_alpha,
                                        cube_edge_size=cube_edge_size
                                        ),
            2: create_energy_applicator((core_material,
                                         Cuboid(
                                             location=Location(x=30, z=2, y=10),
                                             dimensions=core_dimensions)
                                         ),
                                        watts_to_apply=leakage_alpha,
                                        cube_edge_size=cube_edge_size
                                        ),
            3: create_energy_applicator((core_material,
                                         Cuboid(
                                             location=Location(x=10, z=2, y=30),
                                             dimensions=core_dimensions)
                                         ),
                                        watts_to_apply=leakage_alpha,
                                        cube_edge_size=cube_edge_size
                                        ),
            4: create_energy_applicator((core_material,
                                         Cuboid(
                                             location=Location(x=30, z=2, y=30),
                                             dimensions=core_dimensions)
                                         ),
                                        watts_to_apply=leakage_alpha,
                                        cube_edge_size=cube_edge_size
                                        )
        }

        # Internal heat generators
        internal_heat_generators = {
            0: TMInternal(
                cuboid=Cuboid(
                    location=Location(x=10, z=2, y=10),
                    dimensions=core_dimensions),
                boostRateMultiplier=leakage_delta
            ),
            1: TMInternal(
                cuboid=Cuboid(location=Location(x=30, z=2, y=10),
                              dimensions=core_dimensions),
                boostRateMultiplier=leakage_delta
            ),
            2: TMInternal(
                cuboid=Cuboid(location=Location(x=10, z=2, y=30),
                              dimensions=core_dimensions),
                boostRateMultiplier=leakage_delta
            ),
            3: TMInternal(
                cuboid=Cuboid(location=Location(x=30, z=2, y=30),
                              dimensions=core_dimensions),
                boostRateMultiplier=leakage_delta
            )
        }

        # Generate cubed space
        cubed_space = Model(
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
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        temperatures_vector.append(temperature_over_before_zero_seconds)

        # Apply energy over the cubed space
        number_of_iterations = 10
        for i in range(number_of_iterations):
            initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                     external_energy_application_points={0},  # {0, 1, 2, 3, 4},
                                                     # internal_energy_application_points={0, 1, 2, 3},
                                                     amount_of_time=0.5)
            temperature = cubed_space.obtain_temperature(actual_state=initial_state)

            temperatures_vector.append(temperature)

        for i, temperature in enumerate(temperatures_vector):
            # Zero seconds
            plot_3d_heat_map_temperature(temperature,
                                         min_temperature=min_simulation_value,
                                         max_temperature=max_simulation_value).show()

            plot_2d_heat_map(temperature,
                             min_temperature=min_simulation_value,
                             max_temperature=max_simulation_value,
                             axis="Z", location_in_axis=1).show()

            min_temperature = obtain_min_temperature(temperature)
            max_temperature = obtain_max_temperature(temperature)

            print("Temperature before", i * 0.5, "seconds: min", min_temperature, ", max", max_temperature)

    @unittest.skip("Manual visualization test")
    def test_external_conduction_plot(self):
        # Dimensions of the cubes
        cubes_dimensions = Dimensions(x=4, z=4, y=4)

        # Cube 0 material
        cube_0_material = SMSilicon()

        # Cube 1 material
        cube_1_material = SMCooper()

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
            0: (cube_0_material,
                Cuboid(
                    location=Location(x=0, z=0, y=0),
                    dimensions=cubes_dimensions)
                ),
            1: (cube_1_material,
                Cuboid(
                    location=Location(x=cubes_dimensions.x, z=0, y=0),
                    dimensions=cubes_dimensions)
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FEAirForced()

        cubed_space = Model(
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
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.1)
        temperature_over_before_point_one_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.1)
        temperature_over_before_point_two_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

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

        # Point one seconds
        plot_3d_heat_map_temperature(temperature_over_before_point_one_seconds,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value).show()

        plot_2d_heat_map(temperature_over_before_point_one_seconds,
                         min_temperature=min_simulation_value,
                         max_temperature=max_simulation_value, axis="Z", location_in_axis=2).show()

        min_temperature = obtain_min_temperature(temperature_over_before_point_one_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_point_one_seconds)

        print("Temperature before 0.1 seconds: min", min_temperature, ", max", max_temperature)

        # Point two seconds
        plot_3d_heat_map_temperature(temperature_over_before_point_two_seconds,
                                     min_temperature=min_simulation_value,
                                     max_temperature=max_simulation_value).show()

        plot_2d_heat_map(temperature_over_before_point_two_seconds,
                         min_temperature=min_simulation_value,
                         max_temperature=max_simulation_value, axis="Z", location_in_axis=2).show()

        min_temperature = obtain_min_temperature(temperature_over_before_point_two_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_point_two_seconds)

        print("Temperature before 0.2 second: min", min_temperature, ", max", max_temperature)

    @unittest.skip("Manual visualization test")
    def test_external_conduction_plot_2d_3d_animation_generation(self):
        # Dimensions of the cubes
        cubes_dimensions = Dimensions(x=4, z=4, y=4)

        # Cube 0 material
        cube_0_material = SMSilicon()

        # Cube 1 material
        cube_1_material = SMCooper()

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
            0: (cube_0_material,
                Cuboid(
                    location=Location(x=0, z=0, y=0),
                    dimensions=cubes_dimensions)
                ),
            1: (cube_1_material,
                Cuboid(
                    location=Location(x=cubes_dimensions.x, z=0, y=0),
                    dimensions=cubes_dimensions)
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FEAirForced()

        cubed_space = Model(
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
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.1)
        temperature_over_before_point_one_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.1)
        temperature_over_before_point_two_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        heat_map_2d_video = generate_video_2d_heat_map(
            {
                0.0: temperature_over_before_zero_seconds,
                1: temperature_over_before_point_one_seconds,
                2: temperature_over_before_point_two_seconds
            },
            min_temperature=min_simulation_value,
            max_temperature=max_simulation_value, axis="Z", location_in_axis=2, delay_between_frames_ms=100)

        heat_map_3d_video = generate_video_3d_heat_map(
            {
                0.0: temperature_over_before_zero_seconds,
                1: temperature_over_before_point_one_seconds,
                2: temperature_over_before_point_two_seconds
            },
            min_temperature=min_simulation_value,
            max_temperature=max_simulation_value, delay_between_frames_ms=100)

        writer = animation.FFMpegWriter()
        heat_map_2d_video.save("2d_generation.mp4", writer=writer)
        heat_map_3d_video.save("3d_generation.mp4", writer=writer)

    @unittest.skip("Manual visualization test")
    def test_internal_conduction_plot(self):
        # Dimensions of the cubes
        cubes_dimensions = Dimensions(x=2, z=2, y=2)

        # Cube 0 material
        cube_0_material = SMCooper()

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
            0: (cube_0_material,
                Cuboid(
                    location=Location(x=0, z=0, y=0),
                    dimensions=cubes_dimensions)
                )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FEAirForced()

        cubed_space = Model(
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
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.9)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state, amount_of_time=0.9)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state)

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

    @unittest.skip("Manual visualization test")
    def test_external_conduction_plot_3d_stacked(self):
        # Configuration
        # Size of the simulation step
        simulation_step = 0.1

        # Major cycle in seconds
        major_cycle = 1.0

        # Temperature of the system (Celsius degrees)
        system_temperature = 45

        number_of_cores = 1

        # Dimensions of the core
        core_dimensions = Dimensions(x=10, z=2, y=10)

        # Material of the core
        core_material = SMSilicon()

        # Material of the board
        board_material = SMCooper()

        # Environment initial temperature
        environment_temperature = 273.15 + system_temperature

        # CPU distribution
        # XXXXXXX
        # XX0X3XX
        # XX1X4XX
        # XX2X5XX
        # XXXXXXX

        # Definition of the CPU shape and materials
        cpu_definition = {
            # Cores
            0: (core_material,
                Cuboid(
                    location=Location(x=20, z=2, y=10),
                    dimensions=core_dimensions)
                ),

            # Board
            1: (board_material,
                Cuboid(
                    location=Location(x=0, z=0, y=0),
                    dimensions=Dimensions(x=70, z=2, y=70))
                )
        }

        # Edge size pf 0.5 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = FEAirFree()

        external_heat_generators_dynamic_power = {
            0: create_energy_applicator((core_material,
                                         Cuboid(
                                             location=Location(x=20, z=0, y=10),
                                             dimensions=Dimensions(x=10, z=2, y=10))
                                         ),
                                        watts_to_apply=10,
                                        cube_edge_size=cube_edge_size
                                        )
        }

        # Generate cubed space
        cubed_space = Model(
            material_cubes=cpu_definition,
            cube_edge_size=cube_edge_size,
            external_temperature_booster_points=external_heat_generators_dynamic_power,
            internal_temperature_booster_points={},
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            environment_temperature=environment_temperature
        )

        # Initial temperatures
        temperature_measures: Dict[float, Dict[int, PhysicalCuboid]] = {}
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(actual_state=initial_state)

        temperature_measures[0.0] = temperature_over_before_zero_seconds

        actual_applied_externally_energy_points = {0}

        # Apply energy over the cubed space
        for i in range(round(major_cycle / simulation_step)):
            initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                     external_energy_application_points=
                                                     actual_applied_externally_energy_points,
                                                     internal_energy_application_points=set(),
                                                     amount_of_time=simulation_step)
            temperature = cubed_space.obtain_temperature(actual_state=initial_state)
            temperature_measures[i * simulation_step] = temperature

        # Display temperatures
        for i in range(round(major_cycle / simulation_step)):
            time_to_display = i * simulation_step

            min_temperature = min(obtain_min_temperature(temperature_measures[time_to_display]).values())
            max_temperature = max(obtain_max_temperature(temperature_measures[time_to_display]).values())

            plot_3d = plot_3d_heat_map_temperature(temperature_measures[time_to_display],
                                                   min_temperature=min_temperature,
                                                   max_temperature=max_temperature)

            plot_3d.show()


if __name__ == '__main__':
    unittest.main()
