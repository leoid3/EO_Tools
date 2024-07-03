import timezonefinder as tz
import pytz
import datetime

#Custom libraries
from config import *
#Classes
from classes.orbit import Orbit
from classes.satellite import Satellite
from classes.constellation import Constellation
from classes.poi import Point_of_interest
from classes.gs import Ground_station
from classes.mission import Mission

def init_constellation(name, walkerP, walkerT, walkerF, color, sat_model):
    """
    Permet d'initialiser les constellations.
    """
    cons = Constellation(name, walkerP, walkerT, walkerF, color, sat_model)
    return cons

def init_poi(name, long, lat, alt, color):
    """
    Permet d'initialiser les points d'interet.
    """
    tf = tz.TimezoneFinder()
    timezone_str = tf.certain_timezone_at(lat = lat, lng =long)
    if timezone_str is None:
        print("Impossible de trouver la zone temporelle du point, valeur par defaut: Etc/GMT+1")
        poitz = 'Etc/GMT+1'
    else:
        poitz = pytz.timezone(timezone_str)
        dt = datetime.datetime.utcnow()
        print(str(poitz))
        utcoffset = poitz.localize(dt).strftime('%z')
        if (int(utcoffset[1:3]) < 10) and (int(utcoffset[1:3]) > -10):
           tm = 'Etc/GMT'+str(utcoffset[0])+str(utcoffset[2])
        else: 
            tm = 'Etc/GMT'+str(utcoffset[0:3])
        print(tm)

    poi = Point_of_interest(name, alt, tm, color)
    poi.set_coordinate(lat, long)
    #poi.set_sza(sun_zenith_angle(poi.get_coordinate(0)[0], poi.get_coordinate(0)[1], poi.get_altitude(), poi.get_timezone(), poi.get_name()))
    #print(poi.get_sza())
    return poi

def init_gs(name, long, lat, alt, ele, bw, deb, color):
    """
    Permet d'initialiser les stations sol.
    """
    gs = Ground_station(name, lat, long, alt, ele, bw, deb, color)
    return gs

def init_mission(name, ts, tf, type, sza, lst_poi, lst_gs, const, dp = False, t0 = 0 ):
    """
    Permet d'initialiser les missions.
    """
    mission = Mission(name, ts, t0, tf, sza, dp, type)
    for j in range(len(liste_constellation)):
        if liste_constellation[j].get_name() == const:
            mission.add_constellation(liste_constellation[j])
    for i in range(len(lst_gs)):
        mission.add_gs(lst_gs[i])
    for k in range(len(lst_poi)):
        mission.add_poi(lst_poi[k])
        
    return mission

def init_sat(n, sw, dep, col, ty, orb):
    sat = Satellite(n, sw, dep, col, ty, orb)
    return sat

def init_orb(h, e, i, Ω, ω, ν):
    orb = Orbit(h, e, i, Ω, ω, ν)
    return orb

def reset_liste():
    liste_satellite.clear()
    liste_constellation.clear()
    liste_gs.clear()
    liste_poi.clear()
    liste_mission.clear()