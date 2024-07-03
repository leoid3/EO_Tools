from config import *

class Constellation:
    """
    Permet de creer une constellation.
    """
    def __init__(self, n, p, t, f, c, sat):
        self.__name = n
        self.__walkerP = p
        self.__walkerT = t
        self.__walkerF = f
        self.__color = c
        self.__sat_model = sat
        self.__satellite = []
        self.__iraan = 0
        self.__ita = 0

    #Mutateurs
    def set_name(self, n):
        self.__name = n
    def set_walkerP(self, p):
        self.__walkerP = p
    def set_walkerT(self, t):
        self.__walkerT = t
    def set_walkerF(self, f):
        self.__walkerF = f
    def set_color(self, c):
        self.__color = c
    def set_model(self, sat):
        self.__sat_model = sat
    def add_sat(self, sat):
        self.__satellite.append(sat)

    #Accesseur
    def get_name(self):
        return self.__name
    def get_walkerP(self):
        return self.__walkerP
    def get_walkerT(self):
        return self.__walkerT
    def get_walkerF(self):
        return self.__walkerF
    def get_color(self):
        return self.__color
    def get_sat(self, i):
        return self.__satellite[i]
    def get_iraan(self):
        return self.__iraan
    def get_ita(self):
        return self.__ita
    def get_nb_sat_tot(self):
        return len(self.__satellite)
    def get_model(self):
        return self.__sat_model