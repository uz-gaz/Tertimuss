from typing import List, Tuple

from matplotlib import pyplot, cm, colors


def __obtain_color_palette(number_of_colors: int) -> List[Tuple[int, int, int, int]]:
    """
    Return a color palette
    :param number_of_colors: number of colors to return
    :return: the color palette generated
    """
    color_map = pyplot.get_cmap('nipy_spectral')
    c_norm = colors.Normalize(vmin=0, vmax=number_of_colors - 1)
    scalar_map = cm.ScalarMappable(norm=c_norm, cmap=color_map)
    return [scalar_map.to_rgba(i) for i in range(number_of_colors)]
