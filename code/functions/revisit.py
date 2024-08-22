import numpy as np
from config import *


def revisit_over_a_latitude(a, swath_width, depointing, lat_target, nb_sat, inclination):
    """
    Calcule le nombre de revisite au dessus d'une latitude donnée, par jour.
    """
    h=(a-earth_radius)/1000
    right_extension = h * np.tan(np.deg2rad(depointing))
    swath_ext = (swath_width/2)*(1+np.sin(np.deg2rad(depointing)))/1000
    equivalent_swath=2*(right_extension+swath_ext)
    nb_orbit= 86400/(2*np.pi*np.sqrt((a**3)/mu))
    peri = 2*np.pi*earth_radius/1000
    revisit_per_day = (nb_sat*nb_orbit*equivalent_swath)/(peri*np.cos(np.deg2rad(lat_target)))
    
    return revisit_per_day



