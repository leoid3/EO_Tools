from config import *
import numpy as np

class Satellite:
    """
    Permet de creer un satellite.
    """
    def __init__(self, n, sw, dep, col, ty, orb):
        self.__name = n
        self.__swath = sw
        self.__depointing = dep
        self.__color = col
        self.__type = ty
        self.__orbit = orb

        self.__x = []
        self.__y = []
        self.__z = []
        self.__x_ecef = []
        self.__y_ecef = []
        self.__z_ecef = []
        self.__vx = []
        self.__vy = []
        self.__vz = []

    #Mutateurs
    def set_name(self, n):
        self.__name = n
    def set_swath(self, sw):
        self.__swath = sw
    def set_depointing(self, d):
        self.__depointing = d
    def set_color(self, c):
        self.__color = c
    def set_type(self, t):
        self.__type = t
    def set_orbit(self, o):
        self.__orbit = o
    def set_position(self, pos):
        self.__x = np.transpose(pos[:, 0])
        self.__y = np.transpose(pos[:, 1])
        self.__z = np.transpose(pos[:, 2])
    def set_position_ecef(self, pos):
        self.__x_ecef = np.transpose(pos[:, 0])
        self.__y_ecef = np.transpose(pos[:, 1])
        self.__z_ecef = np.transpose(pos[:, 2])
    def set_velocity(self, velo):
        self.__vx = np.transpose(velo[:, 3])
        self.__vy = np.transpose(velo[:, 4])
        self.__vz = np.transpose(velo[:, 5])

    #Accesseurs
    def get_name(self):
        return self.__name
    def get_swath(self):
        return self.__swath
    def get_depoiting(self):
        return self.__depointing
    def get_color(self):
        return self.__color
    def get_type(self):
        return self.__type
    def get_orbit(self):
        return self.__orbit
    def get_position(self):
        return self.__x[:], self.__y[:], self.__z[:]
    def get_position_ecef(self):
        return self.__x_ecef[:], self.__y_ecef[:], self.__z_ecef[:]
    def get_velocity(self):
        return self.__vx[:], self.__vy[:], self.__vz[:]