from typing import Set

from tertimuss_simulation_lib.system_definition import CpuSpecification, EnergyConsumptionProperties, \
    CoreGroupSpecification, MaterialCuboid, generate_automatic_core_origins, BoardSpecification


def generate_default_cpu(number_of_cores: int, available_frequencies: Set[int]) -> CpuSpecification:
    """
    Generate a default CPU specifying the number of cores and the available frequencies
    :param number_of_cores: Number of cores in the CPU
    :param available_frequencies: Available frequencies in the CPU
    :return: CPU specification
    """
    energy_consumption_properties = EnergyConsumptionProperties(leakage_alpha=0.001, leakage_delta=0.1,
                                                                dynamic_alpha=1.52,
                                                                dynamic_beta=0.08)

    core_physical_properties = MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148)

    board_physical_properties = MaterialCuboid(x=50 * (1 + (number_of_cores // 16)),
                                               y=50 * (1 + (number_of_cores // 16)),
                                               z=1, p=8933, c_p=385, k=400)

    cores_origins = generate_automatic_core_origins(0, board_physical_properties.x,
                                                    0, board_physical_properties.y,
                                                    core_physical_properties.x,
                                                    core_physical_properties.y,
                                                    number_of_cores)

    cores_specification = CoreGroupSpecification(
        physical_properties=core_physical_properties,
        energy_consumption_properties=energy_consumption_properties,
        available_frequencies=available_frequencies,
        cores_origins=cores_origins)

    board_specification = BoardSpecification(board_physical_properties)
    return CpuSpecification(board_specification=board_specification, cores_specification=cores_specification)
