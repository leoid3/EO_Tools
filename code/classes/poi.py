class Point_of_interest:
    """
    Permet de creer un point d'interet.
    """
    def __init__(self, n, alt, tm, c, ia):
        self.__name = n
        self.__coordinates = []
        self.__altitude = alt
        self.__timezone = tm
        self.__color = c
        self.__resstep = 0
        self.__isarea = ia
        self.__sza = 0

    #Mutateurs
    def set_name(self, n):
        self.__name = n
    def set_altitude(self, alt):
        self.__altitude = alt
    def set_timezone(self, tm):
        self.__timezone = tm
    def set_color(self, c):
        self.__color = c
    def resestep(self, res):
        self.__resstep = res
    def set_area(self, ia):
        self.__isarea = ia
    def set_coordinate(self, lat, long):
        self.__coordinates.append((lat, long))
    def set_sza(self, sza):
        self.__sza = sza
    def reset_coordinate(self):
        self.__coordinates = []
    #Accesseur
    def get_name(self):
        return self.__name
    def get_altitude(self):
        return self.__altitude
    def get_timezone(self):
        return self.__timezone
    def get_color(self):
        return self.__color
    def get_resstep(self):
        return self.__resstep
    def IsArea(self):
        return self.__isarea
    def get_area(self):
        return self.__coordinates
    def get_coordinate(self, i):
        return self.__coordinates[i]
    def get_sza(self):
        return self.__sza