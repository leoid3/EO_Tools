import csv
from config import *
from functions.initialisation import init_poi, init_gs, init_orb, init_sat, init_constellation

def import_from_csv():
    #POI
    with open('POI.csv', 'r') as file:
        csvreader = csv.DictReader(file)
        for row in csvreader:
            if len(row) == 0:
                print("Nothing on this row")
            else:
                coor = [i.strip() for i in row['coordinate'].split(',')]
                lat = coor[0]
                long = coor[1]
                poi = init_poi(row['name'], float(lat[1:]), float(long[:-1]), float(row['altitude']), row['color'])
                liste_poi.append(poi)
    
    #GS
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
    
    #Satellite+orbit
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
                v= v[:-2]
                orb = init_orb(float(a-6378), float(orbital_element[1]), float(orbital_element[2]), float(orbital_element[3]), float(orbital_element[4]), v)
                sat = init_sat(row['name'], row['swath'], row['depointing'], row['color'], row['type'], orb)
                liste_satellite.append(sat)
    
    #Constellation
    with open('Constellation.csv', 'r') as file:
        csvreader = csv.DictReader(file)
        for row in csvreader:
            if len(row)==0:
                print("skip")
            else:
                for i in range(len(liste_satellite)):
                    if (liste_satellite[i].get_name()) == str(row['satmodel']):
                        sat_model = liste_satellite[i]
                        const = init_constellation(row['name'], row['walkerP'], row['walkerT'], row['walkerF'], row['color'], sat_model)
                        liste_constellation.append(const)

    #Mission
    with open('Mission.csv', 'r') as file:
        csvreader = csv.DictReader(file)
        
        for row in csvreader:
            if len(row)==0:
                print("skip")
            else:
                for i in range(len(liste_constellation)):
                    if (liste_constellation[i].get_name()) == str(row['constellation']):
                        const = liste_constellation[i]
                    else:
                        print("La constellation n'existe pas !")
                        return
                temp = [i.strip() for i in row['gs'].split(',')]
                for j in range(len(temp)):
                    
                print(tempgs[0])