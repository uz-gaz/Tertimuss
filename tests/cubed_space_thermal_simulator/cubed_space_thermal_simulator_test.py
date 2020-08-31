import unittest

from cubed_space_thermal_simulator import MaterialLocatedCube, UnitDimensions, UnitLocation, Material, \
    EnvironmentProperties, ExternalEnergyLocatedCube, InternalEnergyLocatedCube, CubedSpace, ThermalUnits, \
    create_cubed_space, create_initial_state


class CubedSpaceThermalSimulator(unittest.TestCase):
    def test_processor_heat_generation(self):
        # Dimensions of the core
        core_dimensions = UnitDimensions(x=3, y=1, z=3)

        # Material of the core
        core_material = Material(
            density=2330,
            specificHeatCapacities=712,
            thermalConductivity=148
        )

        # Material of the board
        board_material = Material(
            density=8933,
            specificHeatCapacities=385,
            thermalConductivity=400
        )

        # Core initial temperature
        core_initial_temperature = 273.15 + 25

        # Board initial temperature
        board_initial_temperature = 273.15 + 25

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Definition of the CPU shape and materials
        cpu_definition = [
            # Cores
            MaterialLocatedCube(
                location=UnitLocation(x=1, y=2, z=1),
                dimensions=core_dimensions,
                material=core_material
            ),
            MaterialLocatedCube(
                location=UnitLocation(x=6, y=2, z=1),
                dimensions=core_dimensions,
                material=core_material
            ),
            MaterialLocatedCube(
                location=UnitLocation(x=1, y=2, z=6),
                dimensions=core_dimensions,
                material=core_material
            ),
            MaterialLocatedCube(
                location=UnitLocation(x=6, y=2, z=6),
                dimensions=core_dimensions,
                material=core_material
            ),

            # Board
            MaterialLocatedCube(
                location=UnitLocation(x=0, y=0, z=0),
                dimensions=UnitDimensions(x=10, y=2, z=10),
                material=board_material
            )
        ]

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = EnvironmentProperties(
            environmentConvectionFactor=0.001,
            environmentTemperature=environment_temperature
        )

        # CPU energy consumption configuration
        #  Dynamic power = dynamic_alpha * F^3 + dynamic_beta
        #  Leakage power = current temperature * 2 * leakage_delta + leakage_alpha
        leakage_alpha: float = 0.001
        leakage_delta: float = 0.1
        dynamic_alpha: float = 1.52
        dynamic_beta: float = 0.08

        cpu_frequency: float = 1000

        # External heat generators
        external_heat_generators = [
            # Dynamic power
            ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, y=2, z=1),
                dimensions=core_dimensions,
                energy=dynamic_alpha * (cpu_frequency ** 3) + dynamic_beta,
                period=1
            ),

            # Leakage power
            ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, y=2, z=1),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            ExternalEnergyLocatedCube(
                location=UnitLocation(x=6, y=2, z=1),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, y=2, z=6),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            ExternalEnergyLocatedCube(
                location=UnitLocation(x=6, y=2, z=6),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            )
        ]

        # Internal heat generators
        internal_heat_generators = [
            InternalEnergyLocatedCube(
                location=UnitLocation(x=1, y=2, z=1),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            InternalEnergyLocatedCube(
                location=UnitLocation(x=6, y=2, z=1),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            InternalEnergyLocatedCube(
                location=UnitLocation(x=1, y=2, z=6),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            InternalEnergyLocatedCube(
                location=UnitLocation(x=6, y=2, z=6),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            )
        ]

        # Generate cubed space

        cubed_space, cubes_ids, external_heat_generators_ids, internal_heat_generators_ids = create_cubed_space(
            material_cubes=cpu_definition,
            cube_edge_size=cube_edge_size,
            external_energy_application_points=external_heat_generators,
            internal_energy_application_points=internal_heat_generators,
            environment_properties=environment_properties)

        initial_state = create_initial_state(
            cubed_space=cubed_space,
            default_temperature=core_initial_temperature,
            material_cubes_temperatures=None
        )

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            surrounded_cube=None,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_heat_generators=external_heat_generators,
                                                 internal_heat_generators=internal_heat_generators, amount_of_time=1)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            surrounded_cube=None,
                                                                            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_heat_generators=external_heat_generators,
                                                 internal_heat_generators=internal_heat_generators, amount_of_time=1)
        temperature_over_before_two_seconds = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             surrounded_cube=None,
                                                                             units=ThermalUnits.CELSIUS)


if __name__ == '__main__':
    unittest.main()
