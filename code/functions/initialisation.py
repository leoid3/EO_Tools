import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

#Custom libraries
from config import *
from functions.oe_to_sv import orbital_elements_to_state_vectors
from functions.solver import runge_kutta_4, deriv
from functions.orbit_3D import plot_orbit_3d, show_sat
from functions.revisit import revisitV2
from functions.ground_track import plot_ground_track
from functions.sun_zenith_angle import sun_zenith_angle
from functions.export import export_to_csv

#Classes
from classes.orbit import Orbit
from classes.satellite import Satellite
from classes.constellation import Constellation
from classes.poi import Point_of_interest
from classes.gs import Ground_station
from classes.mission import Mission

def init_constellation(ax_3D, ax_2D):
    """
    Permet d'initialiser les constellations.
    """
    cons_list = []
    for i, const in enumerate(constellation):
        cons = Constellation(const['Name'], const['ID'], const['nb_plan'], const['nb_sat'], 360/const['nb_plan'], 360/const['nb_sat'], const['color'])

        for m in range(cons.get_nb_plan()):
            if m==0:
                Ω=cons.get_iraan()
            else:
                Ω=Ω+cons.get_raanoffset()
            for l in range(cons.get_nb_sat()):
                if l==0:
                    ν=cons.get_ita()
                else:
                    ν=ν+cons.get_true_anomalyoffset()

                orb = Orbit(const['altitude'], const['e'], const['i'], Ω, const['ω'], ν)
                #orb = Orbit(a, e, i, Ω, ω, ν)
                sat = Satellite(const['sat_name'], const['swath_width'], const['depointing'], const['color'], const['type'], orb)
                #sat = Satellite(sat_name, const['swath_width'], const['depointing'], const['color'], const['type'], orb)

                #Position initiale
                position, velocity = orbital_elements_to_state_vectors(orb)
                state0 = np.concatenate((position, velocity))
                #Ensemble des solutions
                times, states= runge_kutta_4(deriv, state0, t0, tf, dt)
                sat.set_position(states)
                sat.set_velocity(states)

                show_sat(sat, ax_3D, cons.get_color())
                plot_ground_track(sat, times, ax_2D, cons.get_color())
                cons.add_sat(sat)
    
            plot_orbit_3d(sat, ax_3D, cons.get_name(), cons.get_color())
        cons_list.append(cons)
    return cons_list

def init_poi(ax_2D):
    """
    Permet d'initialiser les points d'interet.
    """
    poi_list = []
    for j, POI in enumerate(Pointofinterest) :
        poi = Point_of_interest(POI['name'], POI['altitude'], POI['timezone'], POI['color'], POI['area'])
        poi.set_coordinate(POI['latitude'], POI['longitude'])
        ax_2D.plot(poi.get_coordinate(0)[1], poi.get_coordinate(0)[0], 'x', label=poi.get_name(), color=poi.get_color())
        ax_2D.legend()
        poi.set_sza(sun_zenith_angle(poi.get_coordinate(0)[0], poi.get_coordinate(0)[1], poi.get_altitude(), poi.get_timezone(), poi.get_name()))
        print(poi.get_sza())
        poi_list.append(poi)
    return poi_list

def init_gs(ax_2D):
    """
    Permet d'initialiser les stations sol.
    """
    gs_list = []
    for k, GS in enumerate(Groundstation):
        gs = Ground_station(GS['name'], GS['latitude'], GS['longitude'], GS['altitude'], GS['elevation'], GS['bandwidth'], GS['debit'], GS['color'])
        ax_2D.plot(gs.get_coordinate()[1], gs.get_coordinate()[0], 'o', label=gs.get_name(), color=gs.get_color())
        ax_2D.legend()
        gs_list.append(gs)
    return gs_list

def init_mission():
    """
    Permet d'initialiser les missions.
    """
    mission_list = []
    for i, miss in enumerate(Missions):
        mission = Mission(miss['name'], miss['TS'], miss['TI'], miss['TF'], miss['sza_min'], miss['depointing'], miss['type'])
        mission_list.append(mission)
    return mission_list

def init_plot():
    """
    Permet d'initialiser les differents plot.
    """    
    fig_3D = plt.figure()
    ax_3D = fig_3D.add_subplot(111, projection='3d')
    ax_3D.plot([0], [0], [0], 'o', label='Terre', markersize=12)

    fig_2D = plt.figure()
    ax_2D = fig_2D.add_subplot(111, projection=ccrs.PlateCarree())
    ax_2D.stock_img()
    plot = plt
    return ax_3D, ax_2D, plot