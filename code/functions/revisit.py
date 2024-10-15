import numpy as np
from config import *


def revisit_over_a_latitude(a, swath_width, depointing, lat_target, nb_sat, inclination):
    """
    Calcule le nombre de revisite au dessus d'une latitude donnée, par jour.
    """
    if inclination > 90:
        inclination = 90 - (inclination-90)
    
    if lat_target < inclination:
        h=(a-earth_radius)/1000
        right_extension = h * np.tan(np.deg2rad(depointing))
        swath_ext = (swath_width/2)*(1+np.sin(np.deg2rad(depointing)))/1000
        equivalent_swath=2*(right_extension+swath_ext)
        nb_orbit= 86400/(2*np.pi*np.sqrt((a**3)/mu))
        peri = 2*np.pi*earth_radius/1000
        revisit_per_day = (nb_sat*nb_orbit*equivalent_swath)/(peri*np.cos(np.deg2rad(lat_target)))
    else:
        print("L'inclinaison de l'orbite ne permet pas de survoler cette latitude")
        revisit_per_day = 0
    
    return revisit_per_day


def revi(a, inclinaison, latitude):
    if inclinaison > 90:
        inclinaison = 90 - (inclinaison-90)

    lat_max = inclinaison
    if latitude < lat_max:
        period = 2*np.pi*np.sqrt((a**3)/mu)
        nb_orbit = 86400/period
        delta_theta = (360/86400)*period
        coverage_density = nb_orbit*(np.cos(latitude)/np.cos(inclinaison))
        nb_before_rev = 360/delta_theta
        revisit_time = period/(1-(period/86400)*np.cos(inclinaison))
        print(revisit_time)
        return revisit_time
    else:
        print("L'inclinaison de l'orbite ne permet pas de survoler cette latitude")
        return 0


