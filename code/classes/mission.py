from config import *

class Mission:
    """
    Permet de creer une mission.
    """
    def __init__(self, n, ts, t0, tf, sza, dp, t):
        self.__name = n
        self.__timestep = ts
        self.__T0 = t0
        self.__TF = tf
        self.__minsza = sza
        self.__depointing = dp
        self.__type = t
        self.__constellation = []
        self.__poi = []
        self.__gs = []

    #Mutateurs
    def set_name(self, n):
        self.__name = n
    def set_timestep(self, ts):
        self.__timestep = ts
    def set_T0(self, t0):
        self.__T0 = t0
    def set_TF(self, tf):
        self.__TF = tf
    def set_minsza(self, sza):
        self.__minsza = sza
    def set_depointing(self, dp):
        self.__depointing = dp
    def set_type(self, t):
        self.__type = t
    def add_constellation(self, cons):
        self.__constellation.append(cons)
    def add_poi(self, poi):
        self.__poi.append(poi)
    def add_gs(self, gs):
        self.__gs.append(gs)

    #Accesseur
    def get_name(self):
        return self.__name
    def get_timestep(self):
        return self.__timestep
    def get_T0(self):
        return self.__T0
    def get_TF(self):
        return self.__TF
    def get_minsza(self):
        return self.__minsza
    def get_depointing(self):
        return self.__depointing
    def get_type(self):
        return self.__type
    def get_constellation(self, i):
        return self.__constellation[i]
    def get_poi(self, i):
        return self.__poi[i]
    def get_gs(self, i):
        return self.__gs[i]