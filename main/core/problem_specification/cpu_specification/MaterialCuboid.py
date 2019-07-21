class MaterialCuboid(object):
    """
    Material object with cuboid' shape
    """

    def __init__(self, x: float, y: float, z: float, p: float, c_p: float, k: float):
        """

        :param x: X coordinate size (mm)
        :param y: Y coordinate size (mm)
        :param z: Z coordinate size (mm)
        :param p: Density (Kg/cm^3)
        :param c_p: Specific heat capacities (J/Kg K)
        :param k: Thermal conductivity (W/m ºC)
        """
        self.x = x
        self.y = y
        self.z = z
        self.p = p
        self.c_p = c_p
        self.k = k