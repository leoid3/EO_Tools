import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from config import *
from functions.oe_to_sv import orbital_elements_to_state_vectors
from functions.solver import runge_kutta_4, deriv
from functions.orbit_3D import plot_orbit_3d, show_sat
from functions.ground_track import plot_ground_track, show_gs_on_ground_track, show_poi_on_ground_track


def calcul_traj(mission, map):
    """
    Permet de calculer l'obite et de l'afficher.
    """
    const = mission.get_constellation()
    temp_sat = const.get_model()
    temp_orbit = temp_sat.get_orbit()

    fig3d = plt.figure()
    ax_3D = fig3d.add_subplot(111, projection='3d')
    ax_3D.plot([0], [0], [0], 'o', label='Terre', markersize=12)

    fig2d = plt.figure()
    ax_2D = fig2d.add_subplot(111, projection=ccrs.PlateCarree())
    ax_2D.stock_img()

    liste_ta =[]
    t0=0
    delta = mission.get_TF() - mission.get_T0()
    if delta.days==0:
        tf=86400
        dt=mission.get_timestep()
    else:
        tf=3600*24*delta.days
        dt=3600*24*mission.get_timestep()

    for i in range(int(const.get_walkerP())):
        walkerT = const.get_walkerT()
        walkerP = const.get_walkerP()
        walkerF = const.get_walkerF()
        if i == 0:
            Ω = temp_orbit.get_raan()
        else:
            Ω = Ω + 360/walkerP
        for j in range(int(round(walkerT/walkerP))):
            if j==0:
                ta = temp_orbit.get_true_ano()
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

            temp_orbit.set_true_ano(ta)
            temp_orbit.set_raan(Ω)
            temp_sat.set_orbit(temp_orbit)
            
            position, velocity = orbital_elements_to_state_vectors(temp_sat.get_orbit())
            state0 = np.concatenate((position, velocity))
            #Ensemble des solutions
            times, states= runge_kutta_4(deriv, state0, t0, tf, dt)
            temp_sat.set_position(states)
            temp_sat.set_velocity(states)
            const.add_sat(temp_sat)

            show_sat(temp_sat, ax_3D)
            plot_ground_track(temp_sat, times, ax_2D, const.get_color(), map)
        plot_orbit_3d(temp_sat, ax_3D, const.get_name(), const.get_color(), delta)
    mission.add_constellation(const)

    for i in range(mission.get_nb_poi()):
        show_poi_on_ground_track(mission.get_poi(i), ax_2D)
    for i in range(mission.get_nb_gs()):
        show_gs_on_ground_track(mission.get_gs(i), ax_2D)
    plt.show()