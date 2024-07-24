import csv
from tkinter.messagebox import showinfo
from datetime import datetime
from config import *
from functions.initialisation import init_poi, init_gs, init_orb, init_sat, init_constellation, init_mission, reset_liste

def import_from_csv():
    """
    Permet d'importer les données de simulation depuis un fichier .csv.
    """
    reset_liste()
    er=0
    #POI
    try:
        with open('POI.csv', 'r') as file:
            
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if len(row) == 0:
                    print("Nothing on this row")
                else:
                    coord = [i.strip() for i in row['coordinate'].split(',')]
                    if row['area'] == 'False':
                        lat = coord[0]
                        long = coord[1]
                        coordinate = (float(lat[1:]), float(long[:-1]))
                    else:
                        coordinate=[]
                        for j in range(len(coord)):
                            if j==0:
                                lat = coord[0]
                                long = coord[1]
                                try:
                                    float(lat[2:])
                                    coordinate.append((float(lat[2:]), float(long[:-1])))
                                except ValueError:
                                    coordinate.append((float(lat[3:]), float(long[:-1]))) 
                            elif j== len(coord)-2:
                                lat = coord[j]
                                long= coord[j+1]
                                try:
                                    float(long[:-2])
                                    coordinate.append((float(lat[1:]), float(long[:-2])))
                                except ValueError:
                                    coordinate.append((float(lat[1:]), float(long[:-3])))
                            elif j%2==0:
                                lat = coord[j]
                                long = coord[j+1]
                                coordinate.append((float(lat[1:]), float(long[:-1])))
                    print(len(coordinate))
                    poi = init_poi(row['name'], coordinate, float(row['altitude']), row['color'], row['area'] == 'True')
                    liste_poi.append(poi)
            showinfo("Message", 'POI imported')
    except FileNotFoundError:
        showinfo("Error", 'The file containing POIs data does not exist')
        er +=1
    
    #GS
    try:
        with open('GS.csv', 'r') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if len(row)==0:
                    print("skip")
                else:
                    coor = [i.strip() for i in row['coordinate'].split(',')] 
                    lat = coor[0]
                    long = coor[1]
                    gs = init_gs(row['name'], float(long[:-1]), float(lat[1:]), float(row['altitude']), float(row['elevation']), float(row['bandwidth']), float(row['debit']), row['color'])
                    liste_gs.append(gs)
            showinfo("Message", 'GS imported')
    except FileNotFoundError:
        showinfo("Error", 'The file containing GSs data does not exist')
        er +=1
    
    #Satellite+orbit
    try:
        with open('Satellites.csv', 'r') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if len(row)==0:
                    print("skip")
                else:
                    orbital_element = [i.strip() for i in row['orbit'].split(',')]
                    a = orbital_element[0]
                    a= float(a[2:])
                    v = orbital_element[5]
                    v= float(v[:-2])
                    orb = init_orb(float(a-6378e3)/1000, float(orbital_element[1]), float(orbital_element[2]), float(orbital_element[3]), float(orbital_element[4]), v)
                    sat = init_sat(row['name'], row['swath'], row['depointing'], row['color'], row['type'], orb)
                    liste_satellite.append(sat)
            showinfo("Message", 'Satellite imported')
    except FileNotFoundError:
        showinfo("Error", 'The file containing Satellites data does not exist')
        er +=1
    
    #Constellation
    try:
        with open('Constellation.csv', 'r') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if len(row)==0:
                    print("skip")
                else:
                    for i in range(len(liste_satellite)):
                        if (liste_satellite[i].get_name()) == str(row['satmodel']):
                            sat_model = liste_satellite[i]
                            const = init_constellation(row['name'], int(float(row['walkerP'])), int(float(row['walkerT'])), int(float(row['walkerF'])), row['color'], sat_model)
                            liste_constellation.append(const)
            showinfo("Message", 'Constellation imported')
    except FileNotFoundError:
        showinfo("Error", 'The file containing Constellations data does not exist')
        er +=1

    #Mission
    try:
        with open('Mission.csv', 'r') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if len(row)==0:
                    print("skip")
                else:
                    temp_gs = []
                    temp_poi=[]
                    for i in range(len(liste_constellation)):
                        if (liste_constellation[i].get_name()) == str(row['constellation']):
                            const = liste_constellation[i]
                        else:
                            print("La constellation n'existe pas !")
                            
                    temp = [i.strip() for i in row['gs'].split(',')]
                    for j in range(len(temp)):
                        if len(temp)==1:
                            u = temp[j]
                            u=u[2:]
                            u=u[:-2]
                        elif j==0:
                            u = temp[j]
                            u=u[2:]
                            u=u[:-1]
                        elif j== len(temp)-1:
                            u = temp[j]
                            u=u[1:]
                            u=u[:-2]
                        else:
                            u = temp[j]
                            u=u[1:]
                            u=u[:-1]
                        for k in range(len(liste_gs)):
                            if liste_gs[k].get_name() == u:
                                temp_gs.append(liste_gs[k])
                                print("done GS")
                    temp = [i.strip() for i in row['poi'].split(',')]
                    for j in range(len(temp)):
                        if len(temp)==1:
                            u = temp[j]
                            u=u[2:]
                            u=u[:-2]
                        elif j==0:
                            u = temp[j]
                            u=u[2:]
                            u=u[:-1]
                        elif j== len(temp)-1:
                            u = temp[j]
                            u=u[1:]
                            u=u[:-2]
                        else:
                            u = temp[j]
                            u=u[1:]
                            u=u[:-1]
                        for k in range(len(liste_poi)):
                            if liste_poi[k].get_name() == u:
                                temp_poi.append(liste_poi[k])
                                print("done poi")
                    ti = datetime.strptime(row['starttime'], '%Y-%m-%d').date()
                    te = datetime.strptime(row['endtime'], '%Y-%m-%d').date()
                    miss = init_mission(row['name'], int(float(row['timestep'])),ti, te, row['type'], float(row['minsza']), temp_poi, temp_gs, const.get_name())
                    liste_mission.append(miss)
            showinfo("Message", 'Mission imported')
    except FileNotFoundError:
        showinfo("Error", 'The file containing Missions data does not exist')
        er +=1
    return er
                    
                