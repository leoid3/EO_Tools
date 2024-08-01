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
    Permet de calculer le sza d'un point à une heure précise.
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
    
    plt.figure(figsize=(10, 6))
    plt.plot(time_range, zenith_angle, label='Sun zenith angle', color='blue')
    plt.xlabel('Times (UTC)')
    plt.ylabel('Sun zenith angle (°)')
    plt.title(f"Evolution of the sun zenith angle at {name}")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return zenith_angle, time_range