class Ground_station:
    """
    Permet de creer une station sol.
    """
    def __init__(self, n, lat, long, alt, e, bw, d, ant, c):
        self.__name = n
        self.__latitude = lat
        self.__longitude = long
        self.__elevation = e
        self.__band = bw
        self.__debit = d
        self.__antenna = ant
        self.__altitude = alt
        self.__color = c
    
    #Mutateurs
    def set_name(self, n):
        self.__name = n
    def set_latitude(self, lat):
        self.__latitude = lat
    def set_longitude(self, long):
        self.__longitude = long
    def set_elevation(self, e):
        self.__elevation = e
    def set_band(self, bw):
        self.__band = bw
    def set_altitude(self, alt):
        self.__altitude = alt
    def set_debit(self, d):
        self.__debit = d
    def set_color(self, c):
        self.__color = c
    def set_antenna(self, a):
        self.__antenna = a
    
    #Accesseurs
    def get_name(self):
        return self.__name
    def get_coordinate(self):
        return self.__latitude, self.__longitude
    def get_elevation(self):
        return self.__elevation
    def get_band(self):
        return self.__band
    def get_altitude(self):
        return self.__altitude
    def get_debit(self):
        return self.__debit
    def get_color(self):
        return self.__color
    def get_antenna(self):
        return self.__antenna