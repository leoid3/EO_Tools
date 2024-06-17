import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from config import *
from oe_to_sv import orbital_elements_to_state_vectors
from solver import runge_kutta_4, deriv
from orbit_3D import plot_orbit_3d, show_sat
from revisit import revisitV2
from ground_track import plot_ground_track
from sun_zenith_angle import sun_zenith_angle

fig_3D = plt.figure()
ax_3D = fig_3D.add_subplot(111, projection='3d')
ax_3D.plot([0], [0], [0], 'o', label='Terre', markersize=12)

fig_2D = plt.figure()
ax_2D = fig_2D.add_subplot(111, projection=ccrs.PlateCarree())
ax_2D.stock_img()

for i, const in enumerate(constellation):
    for m in range(const['nb_plan']):
        if m==0:
            Ω=const['Ω']
        else:
            Ω=Ω+360/const['nb_plan']
        for l in range(const['nb_sat']):
            if l==0:
                ν=const['ν']
            else:
                ν=ν+360/const['nb_sat']
            position, velocity = orbital_elements_to_state_vectors(const['a'], const['e'], const['i'], Ω, const['ω'], ν)
            state0 = np.concatenate((position, velocity))
            times, states= runge_kutta_4(deriv, state0, t0, tf, dt)
            show_sat(states, ax_3D, l, const['ID'], const['color'])
            plot_ground_track(states, times, ax_2D, l, const['ID'], const['color'])
    
        plot_orbit_3d(states, ax_3D, const['ID'], const['color'])

    for j, POI in enumerate(Point_of_interest) :
        revisit=revisitV2(const['a'], const['swath_width'], const['depointing'], POI['latitude'], POI['longitude'], const['nb_sat'])
        print('Il y a une revisite de '+str(revisit)+' au dessus de '+POI['name']+' pour la constellation '+str(const['ID']))


for k, POI in enumerate(Point_of_interest):
    sza = sun_zenith_angle(POI['latitude'], POI['longitude'], POI['altitude'], POI['timezone'], POI['name'])
    print(sza)
    ax_2D.plot(POI['longitude'], POI['latitude'], 'x', color=POI['color'], label=POI['name'])

plt.show()