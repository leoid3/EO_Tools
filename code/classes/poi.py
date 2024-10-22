import numpy as np
class Point_of_interest:
    """
    Permet de creer un point d'interet.
    """
    def __init__(self, n, alt, tm, c, ia):
        self.__name = n
        self.__coordinates = []
        self.__grid = []
        self.__poly = []
        self.__altitude = alt
        self.__timezone = tm
        self.__color = c
        self.__resstep = 0
        self.__isarea = ia
        self.__sza = 0
        self.__multi = False

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
    def set_grid(self, g):
        self.__grid = g
    def set_poly(self, p):
        self.__poly = p
    def set_coordinate(self, lat, long):
        self.__coordinates.append((lat, long))
    def set_sza(self, sza):
        self.__sza = sza
    def reset_coordinate(self):
        self.__coordinates = []
    def set_multi(self):
        self.__multi = True
    def set_multipoly(self, area):
        self.reset_coordinate()
        corrected_poly = []
        j=0
        for i in range(len(area)):
            if i < len(area)-1:
                xi = np.abs(area[i][1])
                yi = np.abs(area[i][0])
                xf = np.abs(area[i+1][1])
                yf = np.abs(area[i+1][0])   
            if i== len(area):
                xi = np.abs(area[i][1])
                yi = np.abs(area[i][0])
                xf = np.abs(area[0][1])
                yf = np.abs(area[0][0])
            dist = np.sqrt((xf-xi)**2+(yf-yi)**2)
            if dist > 1:
                poly = []
                for q in range(j, i+1):
                    poly.append((area[q][0], area[q][1]))
                corrected_poly.append(poly)
                j = q+1

        self.__coordinates = corrected_poly
                

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
    def get_grid(self):
        return self.__grid
    def get_poly(self):
        return self.__poly
    def get_coordinate(self, i):
        return self.__coordinates[i]
    def get_sza(self):
        return self.__sza
    def get_multi(self):
        return self.__multi
    