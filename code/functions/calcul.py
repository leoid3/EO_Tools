import numpy as np
from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import timedelta
import pandas as pd
import pvlib
from pvlib.location import Location
from config import *
import time, os
from shapely.geometry import Polygon
from shapely.prepared import prep
from functions.oe_to_sv import orbital_elements_to_state_vectors
from functions.solver import runge_kutta_4, deriv
from functions.orbit_3D import plot_orbit_3d, show_sat
from functions.ground_track import plot_ground_track, show_gs_on_ground_track, show_poi_on_ground_track
from functions.initialisation import init_orb, init_sat
from functions.coordinates_converter import ECEF_to_ENU


def calcul_traj(mission, map):
    """
    Permet de calculer l'obite et de l'afficher.
    """
    start_time = time.time()
    const = mission.get_constellation()

    fig3d = plt.figure(figsize=(10, 10))
    ax_3D = fig3d.add_subplot(111, projection='3d')
    ax_3D.plot([0], [0], [0], 'o', label='Terre', markersize=12)

    fig2d = plt.figure(figsize=(10, 10))
    ax_2D = fig2d.add_subplot(111, projection=ccrs.PlateCarree())
    ax_2D.stock_img()

    for i in range(mission.get_nb_poi()):
        show_poi_on_ground_track(mission.get_poi(i), ax_2D)
    for i in range(mission.get_nb_gs()):
        show_gs_on_ground_track(mission.get_gs(i), ax_2D)

    liste_marker =[]
    liste_ta =[]
    
    delta, t0, tf, dt = simulation_time(mission)

    for i in range(int(const.get_walkerP())):
        walkerT = const.get_walkerT()
        walkerP = const.get_walkerP()
        walkerF = const.get_walkerF()
        temp_sat = const.get_model()
        temp_orbit = temp_sat.get_orbit()
        a_mod, e_mod, i_mod, Ω_mod, ω_mod, ν_mod = temp_orbit.get_all()
        new_orbit = init_orb((a_mod-6378e3)/1000, e_mod, i_mod, Ω_mod, ω_mod, ν_mod)

        if i == 0:
            Ω = new_orbit.get_raan()
        else:
            Ω = Ω + 360/walkerP
        for j in range(int(round(walkerT/walkerP))):
            
            if j==0:
                ta = new_orbit.get_true_ano()
            else:
                 ta = ta + 360/(int(round(walkerT/walkerP)))
            if i==0:
                liste_ta.append(ta)
            else:
                if (walkerF+j) <= (len(liste_ta)-1):
                    k = walkerF+j
                    ta = liste_ta[int(k)]
                else:
                    k = (walkerF+j) - len(liste_ta)
                    ta = liste_ta[int(k)]

            new_orbit.set_true_ano(ta)
            new_orbit.set_raan(Ω)
            new_sat= init_sat(temp_sat.get_name()+f"-{j+1}-{i+1}", temp_sat.get_swath(), temp_sat.get_depoiting(), temp_sat.get_color(), temp_sat.get_type(), new_orbit)
            
            position, velocity = orbital_elements_to_state_vectors(new_sat.get_orbit())
            state0 = np.concatenate((position, velocity))
            #Ensemble des solutions
            times, states= runge_kutta_4(deriv, state0, t0, tf, dt)
            new_sat.set_position(states)
            new_sat.set_velocity(states)
            const.add_sat(new_sat)

            show_sat(new_sat, ax_3D)
            marker_pos= plot_ground_track(new_sat, times, ax_2D, const.get_color(), map)
            liste_marker.append(marker_pos)
            plot_orbit_3d(new_sat, ax_3D, const.get_name(), const.get_color(), delta)
    mission.add_constellation(const)

    end_time = time.time()
    print(f"Elapsed time : {end_time - start_time} s")
    box = ax_2D.get_position()
    ax_2D.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax_2D.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    box = ax_3D.get_position()
    ax_3D.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax_3D.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    mission_folder = result_folder / mission.get_name()
    if not os.path.exists(mission_folder):
        os.makedirs(mission_folder)

    fig2d.savefig(mission_folder / f"Ground Track of {mission.get_name()}.png", bbox_inches='tight')
    fig3d.savefig(mission_folder / f"Orbit of {mission.get_name()}.png", bbox_inches='tight')

    plt.show()

    return liste_marker

def kepler_equation(E, M, e):
    return E - e * np.sin(E) - M

def kepler_equation_prime(E, e):
    return 1 - e * np.cos(E)

def solve_kepler(M, e, tol=1e-6, max_iter=1000):
    E = M if e < 0.8 else np.pi
    for _ in range(max_iter):
        f = kepler_equation(E, M, e)
        f_prime = kepler_equation_prime(E, e)
        E_new = E - f / f_prime
        if abs(E_new - E) < tol:
            return E_new
        E = E_new
    raise RuntimeError("La méthode de Newton-Raphson n'a pas convergé")

def true_anomaly(M, e):
    E = solve_kepler(M, e)
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    return nu

def simulation_time(mission):
    """
    Permet de calculer le temps total de la simulation.
    """
    t0=0
    dt=mission.get_timestep()
    delta = mission.get_TF() - mission.get_T0()
    if delta.days==0:
        tf=86400
    else:
        tf=3600*24*delta.days

    return delta, t0, tf, dt

def calcul_swath(sat):
    """
    Permet de calculer la fauchée projetée au sol su satellite.
    """
    swath = sat.get_swath()
    depointing = sat.get_depoiting()
    orb = sat.get_orbit()
    a = orb.get_semi_major_axis()
    h=(a-earth_radius)/1000
    rigth_extension = h * np.tan(np.deg2rad(depointing))
    swath_ext = (swath/2)*(1+np.sin(np.deg2rad(depointing)))/1000
    equivalent_swath=2*(rigth_extension+swath_ext)

    return equivalent_swath

def gs_interval(x, y, z, lat, long, ele, gsx, gsy, gsz, dt, time):
    """
    Permet de calculer l'intervale de temps de visibilité.
    """
    angle_list = []
    interval = []
    time_inter = []
    for j in range(len(x)):
        enu_vector = ECEF_to_ENU(x[j], y[j], z[j], lat, long, gsx, gsy, gsz)
        E, N, U = enu_vector
        angle = np.arcsin(U / np.sqrt(E**2 + N**2 + U**2)) * (180 / np.pi)
        angle_list.append(float(angle))
            #Recupère le temps pour lequel angle>ele
    for j in range(len(angle_list)):
        if angle_list[j]>ele:
            time_inter.append(time[j])
                    
            #Cree un tableau d'interval de temps
    for j in range(len(time_inter) - 1):
        if j == 0:
            t0=time_inter[0]
        if (time_inter[j+1]-time_inter[j])>dt:
            tf = time_inter[j]
            interval.append((t0, tf))
            t0 = time_inter[j+1]
        if j == len(time_inter) - 2:
            tf = time_inter[j+1]
            interval.append((t0, tf))
    return interval, angle_list

def poi_interval(x, y, z, lat, long, poix, poiy, poiz, swath, dt, time):
    """
    Permet de calculer l'intervale de temps de visibilité.
    """
    distance_list =[]
    time_inter = []
    angle_list = []
    interval = []
    for j in range(len(x)):
        enu_vector = ECEF_to_ENU(x[j], y[j], z[j], lat, long, poix, poiy, poiz)
        E, N, U = enu_vector
        angle = np.arcsin(U / np.sqrt(E**2 + N**2 + U**2)) * (180 / np.pi)
        angle_list.append(float(angle))
        distance = np.sqrt(E**2 + N**2)
        distance_list.append(distance)
    for j in range(len(angle_list)):
        if (angle_list[j] > 0) and (distance_list[j] < swath):
            time_inter.append(time[j])
    for j in range(len(time_inter) - 1):
        if j == 0:
            t0=time_inter[0]
        if (time_inter[j+1]-time_inter[j])>dt:
            tf = time_inter[j]
            interval.append((t0, tf))
            t0 = time_inter[j+1]
        if j == len(time_inter) - 2:
            tf = time_inter[j+1]
            interval.append((t0, tf))
    return interval, angle_list  

def poi_grid(x, y, z, lat, long, poix, poiy, poiz, swath, miss, tm, name, alt):
    angle_list = []
    distance_list = []
    visible = False
    sza = False
    zenith_angle, _ = sun_zenith_angle(miss, lat, long, alt, tm, name)
    liste_sza = zenith_angle['elevation']
    for j in range(len(x)):
        enu_vector = ECEF_to_ENU(x[j], y[j], z[j], lat, long, poix, poiy, poiz)
        E, N, U = enu_vector
        angle = np.arcsin(U / np.sqrt(E**2 + N**2 + U**2)) * (180 / np.pi)
        angle_list.append(float(angle))
        distance = np.sqrt(E**2 + N**2)
        distance_list.append(distance)
    for j in range(len(angle_list)):
        if (angle_list[j] > 0) and (distance_list[j] < swath):
            visible = True
            if liste_sza[j] > miss.get_minsza():
                sza = True
            break
    
    return visible, sza

def grid_bounds(poly, delta):
    """
    Permet de calculer la grille.
    """
    minx, miny, maxx, maxy = poly.bounds
    nx = int((maxx - minx)/delta)
    ny = int((maxy - miny)/delta)
    gx, gy = np.linspace(minx,maxx,nx), np.linspace(miny,maxy,ny)
    grid = []
    for i in range(len(gx)-1):
        for j in range(len(gy)-1):
            poly_ij = Polygon([[gx[i],gy[j]],[gx[i],gy[j+1]],[gx[i+1],gy[j+1]],[gx[i+1],gy[j]]])
            grid.append( poly_ij )
    return grid

def partition(poly):
    """
    Filtre les carré qui sont comprises dans le polygone.
    """
    prepared_geom = prep(poly)
    if poly.area < 0.05:
        return None
    else:
        delta = resolution_step(poly)
        grid = list(filter(prepared_geom.intersects, grid_bounds(poly, delta)))
        return grid

def resolution_step(poly, min_delta=0.01, max_delta=1):
    """
    Permet de calculer dynamiquement la résolution de la grille.
    """
    area = poly.area
    normalized_area = np.log1p(area)/np.log1p(50)
    delta = min_delta + (max_delta - min_delta) * normalized_area
    return delta

def sun_zenith_angle(miss, latitude_target, longitude_target, altitude, time_zone, name):
    """
    Permet de calculer le sza d'un point sur la durée de la mission.
    """
    delta, _, _, dt = simulation_time(miss)
    t0 = miss.get_T0()
    if delta.days ==0:
        tf = miss.get_T0() + timedelta(days=1)
    else:
        tf = miss.get_TF()
    
    site = Location(latitude_target, longitude_target, time_zone, altitude, name)
    time_range = pd.date_range(t0, tf, freq=timedelta(seconds=dt), tz=site.tz)
    solpos = pvlib.solarposition.get_solarposition(time_range, site.latitude, site.longitude, site.altitude, method='nrel_numpy')

    zenith_angle = solpos

    return zenith_angle, time_range