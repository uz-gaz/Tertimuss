import math
from typing import Set, Dict

from tertimuss.cubed_space_thermal_simulator.materials_pack import SMSilicon, SMCooper
from tertimuss.cubed_space_thermal_simulator import Dimensions, Location
from .._processor_specification import Processor, EnergyConsumption, CoreModel, \
    Board, Core


def generate_default_cpu(number_of_cores: int, available_frequencies: Set[int],
                         thermal_dissipation: float = 5) -> Processor:
    """
    Generate a default CPU specifying the number of cores and the available frequencies
    :param number_of_cores: Number of cores in the CPU
    :param available_frequencies: Available frequencies in the CPU
    :param thermal_dissipation: Dissipation of each core in watts when they are with maximum frequency
    :return: CPU specification
    """
    # :param preemption_cost: Cost of preemption in cycles
    # :param migration_cost: Cost of migration in cycles

    max_cpu_frequency: float = max(available_frequencies)
    leakage_alpha: float = 0.001
    leakage_delta: float = 0.1
    dynamic_beta: float = 2
    dynamic_alpha: float = (thermal_dissipation - dynamic_beta) * max_cpu_frequency ** -3

    energy_consumption_properties = EnergyConsumption(leakage_alpha=leakage_alpha, leakage_delta=leakage_delta,
                                                      dynamic_alpha=dynamic_alpha,
                                                      dynamic_beta=dynamic_beta)

    core_type_definition = CoreModel(dimensions=Dimensions(x=10, y=10, z=2),
                                     material=SMSilicon(),
                                     core_energy_consumption=energy_consumption_properties,
                                     available_frequencies=available_frequencies)
    #                                         preemption_cost=preemption_cost

    number_of_columns = math.ceil(math.sqrt(number_of_cores))

    lateral_size = number_of_columns * (3 + 10 + 3)

    board_definition = Board(dimensions=Dimensions(x=lateral_size, y=lateral_size, z=1),
                             material=SMCooper(),
                             location=Location(x=0, y=0, z=0))

    cores_definition: Dict[int, Core] = {}

    for i in range(number_of_cores):
        x_position = (3 + 10 + 3) * (i % number_of_columns) + 3
        y_position = (3 + 10 + 3) * (i // number_of_columns) + 3
        cores_definition[i] = Core(core_type=core_type_definition,
                                   location=Location(x=x_position, y=y_position, z=2))

    return Processor(board_definition=board_definition,
                     cores_definition=cores_definition,
                     measure_unit=0.001)
    #                          migration_costs={(i, j): migration_cost for i in range(number_of_cores) for j in
    #                                           range(number_of_cores) if i != j}
