import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pvlib
from pvlib.location import Location
import matplotlib.dates as mdates
from config import *

def sun_zenith_angle(latitude_target, longitude_target, altitude, time_zone, name):
    """
    Permet de calculer le sza d'un point à une heure précise.
    """
    
    site = Location(latitude_target, longitude_target, time_zone, altitude, name)
    time_range = pd.date_range(TI, TF, freq='h', tz=site.tz)
    solpos = pvlib.solarposition.get_solarposition(time_range, site.latitude, site.longitude, site.altitude, method='nrel_numpy')

    return solpos.loc['2024-06-11 12:00:00'].zenith