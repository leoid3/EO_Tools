import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from config import *
from functions.oe_to_sv import orbital_elements_to_state_vectors
from functions.solver import runge_kutta_4, deriv
from functions.orbit_3D import plot_orbit_3d, show_sat
from functions.ground_track import plot_ground_track, show_gs_on_ground_track, show_poi_on_ground_track
from functions.initialisation import init_orb, init_sat


def calcul_traj(mission, map):
    """
    Permet de calculer l'obite et de l'afficher.
    """
    const = mission.get_constellation()
    #temp_sat = const.get_model()
    #temp_orbit = temp_sat.get_orbit()

    fig3d = plt.figure()
    ax_3D = fig3d.add_subplot(111, projection='3d')
    ax_3D.plot([0], [0], [0], 'o', label='Terre', markersize=12)

    fig2d = plt.figure()
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
    t0=0
    delta = mission.get_TF() - mission.get_T0()
    if delta.days==0:
        tf=86400
        dt=mission.get_timestep()
    else:
        tf=3600*24*delta.days
        dt=3600*24*mission.get_timestep()

    return delta, t0, tf, dt

def calcul_swath(a, depointing, swath):
    h=(a-earth_radius)/1000
    rigth_extension = h * np.tan(np.deg2rad(depointing))
    swath_ext = (swath/2)*(1+np.sin(np.deg2rad(depointing)))/1000
    equivalent_swath=2*(rigth_extension+swath_ext)

    return equivalent_swath