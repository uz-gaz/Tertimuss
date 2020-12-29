import math
from typing import Set, Dict

from ....cubed_space_thermal_simulator.materials_pack import SiliconSolidMaterial, CooperSolidMaterial
from ....simulation_lib.system_definition import ProcessorDefinition, CoreEnergyConsumption, CoreTypeDefinition, \
    UnitDimensions, BoardDefinition, UnitLocation, CoreDefinition


def generate_default_cpu(number_of_cores: int, available_frequencies: Set[int], preemption_cost: int = 0,
                         migration_cost: int = 0, thermal_dissipation: float = 65) -> ProcessorDefinition:
    """
    Generate a default CPU specifying the number of cores and the available frequencies
    :param number_of_cores: Number of cores in the CPU
    :param available_frequencies: Available frequencies in the CPU
    :param preemption_cost: Cost of preemption in cycles
    :param migration_cost: Cost of migration in cycles
    :param thermal_dissipation: Dissipation of each core in watts when they are with maximum frequency
    :return: CPU specification
    """
    max_cpu_frequency: float = max(available_frequencies)
    leakage_alpha: float = 0.001
    leakage_delta: float = 0.1
    dynamic_alpha: float = 55 * max_cpu_frequency ** -3
    dynamic_beta: float = 10

    energy_consumption_properties = CoreEnergyConsumption(leakage_alpha=leakage_alpha, leakage_delta=leakage_delta,
                                                          dynamic_alpha=dynamic_alpha,
                                                          dynamic_beta=dynamic_beta)

    core_type_definition = CoreTypeDefinition(dimensions=UnitDimensions(x=10, y=10, z=2),
                                              material=SiliconSolidMaterial(),
                                              core_energy_consumption=energy_consumption_properties,
                                              available_frequencies=available_frequencies,
                                              preemption_cost=preemption_cost)

    number_of_columns = math.ceil(math.sqrt(number_of_cores))

    lateral_size = number_of_columns * (3 + 10 + 3)

    board_definition = BoardDefinition(dimensions=UnitDimensions(x=lateral_size, y=lateral_size, z=1),
                                       material=CooperSolidMaterial(),
                                       location=UnitLocation(x=0, y=0, z=0))

    cores_definition: Dict[int, CoreDefinition] = {}

    for i in range(number_of_cores):
        x_position = (3 + 10 + 3) * (i % number_of_columns) + 3
        y_position = (3 + 10 + 3) * (i // number_of_columns) + 3
        cores_definition[i] = CoreDefinition(core_type=core_type_definition,
                                             location=UnitLocation(x=x_position, y=y_position, z=2))

    return ProcessorDefinition(board_definition=board_definition,
                               cores_definition=cores_definition,
                               migration_costs={(i, j): migration_cost for i in range(number_of_cores) for j in
                                                range(number_of_cores) if i != j},
                               measure_unit=0.001)
