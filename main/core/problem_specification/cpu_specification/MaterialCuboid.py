class MaterialCuboid(object):

    def __init__(self, x: float, y: float, z: float, p: float, c_p: float, k: float):
        """
        Cuboid-shaped material object

        :param x: X size (mm)
        :param y: Y size (mm)
        :param z: Z size (mm)
        :param p: Density (Kg/cm^3)
        :param c_p: Specific heat capacities (J/Kg K)
        :param k: Thermal conductivity (W/m ºC)
        """
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.p: float = p
        self.c_p: float = c_p
        self.k: float = k
