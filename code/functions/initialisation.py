
#Custom libraries
from config import *
from functions.find_tm import findtimezone, centroid
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

def init_poi(name, coord, alt, color, area):
    """
    Permet d'initialiser les points d'interet.
    """
    if area == False:
        tm = findtimezone(coord)
    else:
        x, y= centroid(coord)
        tm =findtimezone((x, y))


    poi = Point_of_interest(name, alt, tm, color, area)
    if area==False:
        poi.set_coordinate(coord[1], coord[0])
    else:
        for i in range(len(coord)):
            poi.set_coordinate(coord[i][0], coord[i][1])
    #poi.set_sza(sun_zenith_angle(poi.get_coordinate(0)[0], poi.get_coordinate(0)[1], poi.get_altitude(), poi.get_timezone(), poi.get_name()))
    #print(poi.get_sza())
    return poi

def init_gs(name, long, lat, alt, ele, bw, deb, color):
    """
    Permet d'initialiser les stations sol.
    """
    gs = Ground_station(name, lat, long, alt, ele, bw, deb, color)
    return gs

def init_mission(name, ts, ti, te, type, sza, lst_poi, lst_gs, const, dp = False):
    """
    Permet d'initialiser les missions.
    """
    mission = Mission(name, ts, ti, te, sza, dp, type)
    for j in range(len(liste_constellation)):
        if liste_constellation[j].get_name() == const:
            mission.add_constellation(liste_constellation[j])
    for i in range(len(lst_gs)):
        mission.add_gs(lst_gs[i])
    for k in range(len(lst_poi)):
        mission.add_poi(lst_poi[k])
    print(mission.get_TF())
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