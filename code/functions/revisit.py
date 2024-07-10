import numpy as np
from functions.eci_to_ecef import eci_to_ecef


from config import *

def calculate_revisits_with_swath(states, latitude_target, longitude_target, swath_width):
    """
    Calcule le nombre de revisites au-dessus d'une latitude et longitude données, en prenant en compte la fauchée du satellite.
    """
    k = False
    revisits = 0
    for state in states:
        x, y, z = state[:3]
        latitude = np.degrees(np.arcsin(z / np.linalg.norm([x, y, z])))
        longitude = np.degrees(np.arctan2(y, x))  # Calcul de la longitude
        altitude = np.linalg.norm([x, y, z]) - earth_radius
        swath_radius = np.degrees(np.arctan(swath_width / (2 * altitude)))
        if np.isclose(latitude, latitude_target, atol=swath_radius) and k==False:
            revisits += 1
            k=True
        elif np.isclose(latitude, latitude_target, atol=swath_radius) == False:
            k=False
    return revisits

def calculate_revisits_with_swath2(states, times, latitude_target, longitude_target, swath_width):
     revisits = 0
     swath_radius = swath_width / (2 * (earth_radius + 600e3)) * 180 / np.pi  # Convertir la fauchée en degrés
     previous_pass = False
     for state, t in zip(states, times):
         state_ecef = eci_to_ecef(state, t)
         x, y, z = state_ecef[:3]
         latitude = np.degrees(np.arcsin(z / np.linalg.norm([x, y, z])))
         longitude = np.degrees(np.arctan2(y, x))
        
         if (abs(latitude - latitude_target) <= swath_radius):
             if not previous_pass:
                 revisits += 1
                 previous_pass = True
         else:
             previous_pass = False
    
     
     return revisits

def revisitV2(a, swath_width, depointing, lat_target, long_target, nb_sat):
    """
    Calcule le nombre de revisite au dessus d'une latitude donnée.
    """
    h=(a-earth_radius)/1000
    rigth_extension = h * np.tan(np.deg2rad(depointing))
    swath_ext = (swath_width/2)*(1+np.sin(np.deg2rad(depointing)))/1000
    equivalent_swath=2*(rigth_extension+swath_ext)
    nb_orbit= 86400/(2*np.pi*np.sqrt((a**3)/mu))
    peri = 2*np.pi*earth_radius/1000
    revisit = (nb_sat*nb_orbit*equivalent_swath)/(peri*np.cos(np.deg2rad(lat_target)))
    
    return revisit



