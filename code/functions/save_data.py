import csv
from config import *

def save_to_csv(lm, lc, lgs, lpoi, ls):
    """
    Sauvegarde les différentes données.
    """
    
    #Mission
    mission_data = []
    for i in range(len(lm)):
        temp1 = []
        temp2 = []
        for k in range(lm[i].get_nb_poi()):
            poitemp = lm[i].get_poi(k)
            temp1.append(poitemp.get_name())
        for j in range(lm[i].get_nb_gs()):
            gstemp = lm[i].get_gs(j)
            temp2.append(gstemp.get_name())
        temp3 = lm[i].get_constellation()
        mission =[lm[i].get_name(),
                  lm[i].get_T0(),
                  lm[i].get_TF(),
                  lm[i].get_timestep(),
                  lm[i].get_type(),
                  lm[i].get_minsza(),
                    temp1,
                    temp2,
                    temp3.get_name()
                ]
        mission_data.append(mission)
    filename = simulation_folder / "Mission.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(mission_fields)
        csvwriter.writerows(mission_data)
    
    #POI
    POI_data = []
    for i in range(len(lpoi)):
        if lpoi[i].IsArea() == True:
            coord = lpoi[i].get_area()
        else:
            coord = [lpoi[i].get_coordinate(0)[1], lpoi[i].get_coordinate(0)[0]]
        poi = [lpoi[i].get_name(),
               coord,
               lpoi[i].get_altitude(),
               lpoi[i].get_color(),
               lpoi[i].get_timezone(),
               lpoi[i].get_sza(),
               lpoi[i].IsArea()
            ]
        POI_data.append(poi)
    filename = simulation_folder / "POI.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(poi_fields)
        csvwriter.writerows(POI_data)

    #GS
    GS_data = []
    for i in range(len(lgs)):
        gs =[lgs[i].get_name(),
             lgs[i].get_coordinate(),
             lgs[i].get_altitude(),
             lgs[i].get_elevation(),
             lgs[i].get_bandwidth(),
             lgs[i].get_debit(),
             lgs[i].get_color()]
        GS_data.append(gs)
    filename = simulation_folder / "GS.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(gs_fields)
        csvwriter.writerows(GS_data)
    
    #Constellation
    cons_data = []
    for i in range(len(lc)):
        temp = lc[i].get_model()
        cons = [lc[i].get_name(),
                lc[i].get_walkerT(),
                lc[i].get_walkerP(),
                lc[i].get_walkerF(),
                temp.get_name(),
                lc[i].get_color()]
        cons_data.append(cons)
    filename = simulation_folder / "Constellation.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(cons_fields)
        csvwriter.writerows(cons_data)

    #Satellite
    sat_data = []
    for i in range(len(ls)):
        temp4 = ls[i].get_orbit()
        sat = [ls[i].get_name(),
               ls[i].get_swath(),
               ls[i].get_depoiting(),
               ls[i].get_type(),
               ls[i].get_color(),
               [temp4.get_all()]]
        sat_data.append(sat)
    filename = simulation_folder / "Satellites.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(sat_fields)
        csvwriter.writerows(sat_data)