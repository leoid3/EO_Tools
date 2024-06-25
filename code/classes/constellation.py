from config import *

class Constellation:
    """
    Permet de creer une constellation.
    """
    def __init__(self, n, id, nbp, nbs, roff, taoff, c):
        self.__name = n
        self.__ID = id
        self.__nb_plan = nbp
        self.__nb_sat = nbs
        self.__raanoffset = roff
        self.__true_anomalyoffset = taoff
        self.__color = c
        self.__satellite = []
        self.__iraan = 0
        self.__ita = 0

    #Mutateurs
    def set_name(self, n):
        self.__name = n
    def set_ID(self, id):
        self.__ID = id
    def set_nb_plan(self, nbp):
        self.__nb_plan = nbp
    def set_nb_sat(self, nbs):
        self.__nb_sat = nbs
    def set_raanoffset(self, roff):
        self.__raanoffset = roff
    def set_true_anomalyoffset(self, taoff):
        self.__true_anomalyoffset = taoff
    def set_color(self, c):
        self.__color = c
    def add_sat(self, sat):
        self.__satellite.append(sat)

    #Accesseur
    def get_name(self):
        return self.__name
    def get_ID(self):
        return self.__ID
    def get_nb_plan(self):
        return self.__nb_plan
    def get_nb_sat(self):
        return self.__nb_sat
    def get_raanoffset(self):
        return self.__raanoffset
    def get_true_anomalyoffset(self):
        return self.__true_anomalyoffset
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