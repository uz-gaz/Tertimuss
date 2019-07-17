import matplotlib.pyplot as plt

from core.problem_specification.CpuSpecification import CpuSpecification, MaterialCuboid


def generate_automatic_origins_test(cpu_specification: CpuSpecification ):
    board_x = [0, cpu_specification.board.x, cpu_specification.board.x, 0]
    board_y = [0, 0, cpu_specification.board.y, cpu_specification.board.y]
    fig, ax = plt.subplots()
    ax.fill(board_x, board_y, 'b')

    for actual_origin in cpu_specification.cpu_origins:
        cpu_x = [actual_origin.x, actual_origin.x + cpu_specification.cpu_core.x,
                 actual_origin.x + cpu_specification.cpu_core.x, actual_origin.x]
        cpu_y = [actual_origin.y, actual_origin.y, actual_origin.y + cpu_specification.cpu_core.y,
                 actual_origin.y + cpu_specification.cpu_core.y]
        ax.fill(cpu_x, cpu_y, 'r')

    plt.show()


cpu_1: CpuSpecification = CpuSpecification(
    MaterialCuboid(x=50, y=50, z=2, p=0.2, c_p=1.2, k=0.1),
    MaterialCuboid(x=10, y=10, z=2, p=0.2, c_p=1.2, k=0.1),
    2,
    1
)

cpu_2: CpuSpecification = CpuSpecification(
    MaterialCuboid(x=50, y=50, z=2, p=0.2, c_p=1.2, k=0.1),
    MaterialCuboid(x=10, y=10, z=2, p=0.2, c_p=1.2, k=0.1),
    3,
    1
)

generate_automatic_origins_test(cpu_1)
generate_automatic_origins_test(cpu_2)
