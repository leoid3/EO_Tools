from config import *

class Orbit:
    """
    Permet de creer une orbite.
    """
    def __init__(self, h, e, i, Ω, ω, ν):
        self.__a = earth_radius + h*1e3
        self.__e = e
        self.__i = i
        self.__Ω = Ω
        self.__ω = ω
        self.__ν = ν
    
    #Mutateurs
    def set_semi_major_axis(self, h):
        self.__a = earth_radius + h
    def set_eccentricity(self, e):
        self.__e = e
    def set_inclination(self, i):
        self.__i = i
    def set_raan(self, Ω):
        self.__Ω = Ω
    def set_arg_peri(self, ω):
        self.__ω = ω
    def set_true_ano(self, ν):
        self.__ν = ν

    #Accesseurs
    def get_semi_major_axis(self):
        return self.__a
    def get_eccentricity(self):
        return self.__e
    def get_inclination(self):
        return self.__i
    def get_raan(self):
        return self.__Ω
    def get_arg_peri(self):
        return self.__ω
    def get_true_ano(self):
        return self.__ν
    def get_all(self):
        return self.__a, self.__e, self.__i, self.__Ω, self.__ω, self.__ν