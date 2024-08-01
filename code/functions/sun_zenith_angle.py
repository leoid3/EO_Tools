import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pvlib
from pvlib.location import Location
import matplotlib.dates as mdates
from config import *
from functions.calcul import simulation_time
from datetime import timedelta

def sun_zenith_angle(miss, latitude_target, longitude_target, altitude, time_zone, name):
    """
    Permet de calculer le sza d'un point sur la durée de la mission.
    """
    delta, _, _, _ = simulation_time(miss)
    t0 = miss.get_T0()
    if delta.days ==0:
        tf = miss.get_T0() + timedelta(days=1)
    else:
        tf = miss.get_TF()
    
    site = Location(latitude_target, longitude_target, time_zone, altitude, name)
    time_range = pd.date_range(t0, tf, freq='h', tz=site.tz)
    solpos = pvlib.solarposition.get_solarposition(time_range, site.latitude, site.longitude, site.altitude, method='nrel_numpy')

    zenith_angle = solpos['elevation']

    return zenith_angle, time_range