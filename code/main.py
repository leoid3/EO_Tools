from functions.initialisation import init_constellation, init_poi, init_gs, init_plot, init_mission

ax_3D, ax_2D, plot = init_plot()

liste_constellation = init_constellation(ax_3D, ax_2D)
liste_poi = init_poi(ax_2D)
liste_gs = init_gs(ax_2D)
list_mission = init_mission()

plot.show()

#    revisit=revisitV2(const['a'], const['swath_width'], const['depointing'], POI['latitude'], POI['longitude'], const['nb_sat'])
#    print('Il y a une revisite de '+str(revisit)+' au dessus de '+POI['name']+' pour la constellation '+str(const['ID']))

