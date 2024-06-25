#Constantes
G = 6.67430e-11  # Constante gravitationnelle en m^3 kg^-1 s^-2
M = 5.972e24  # Masse de la Terre en kg
mu = G * M  # Paramètre gravitationnel standard pour la Terre en m^3.s^-2
earth_radius = 6378e3 #rayon de la Terre en m
omega_earth = 7.2921159e-5 #vitesse de rotation de la Terre en rad.s^-1


# Initialisation des constellations (A SUPPRIMER QUAND L'INTERFACE SERA PRéSENTE !!)
constellation = [
    {'ID': 1, 'altitude': 618e3, 'e': 0.001, 'i': 98.567, 'Ω': 0, 'ω': 0, 'ν': 0, 'swath_width': 20e3, 'depointing': 45, 'color': 'green', 'type': 'EO', 'nb_sat': 2, 'nb_plan': 1, 'Name' : 'Starlink', 'sat_name': "Sentinel-2A" },
      {'ID': 2, 'altitude': 20000e3, 'e': 0.001, 'i': 20, 'Ω': 0, 'ω': 0, 'ν': 0, 'swath_width': 290e3, 'depointing': 0, 'color': 'red', 'type': 'SAR', 'nb_sat': 2, 'nb_plan': 1, 'Name' : 'Kuiper', 'sat_name' : "Sentinel-2B" }      
]
#Initialisation des points d'interets (A SUPPRIMER QUAND L'INTERFACE SERA PRéSENTE !!)
Pointofinterest =[
    {'ID': 1, 'latitude': 43.60444444 , 'longitude': 1.44388889, 'altitude': 150, 'timezone':'Etc/GMT+1', 'name': 'Toulouse', 'color':'red', 'area': False },
    {'ID': 2, 'latitude': 43.11667 , 'longitude': 131.9, 'altitude': 325.99, 'timezone':'Etc/GMT+10', 'name': 'Vladivostok', 'color':'black', 'area' : True }
]
#Initialisation des stations sol (A SUPPRIMER QUAND L'INTERFACE SERA PRéSENTE !!)
Groundstation =[
    {'ID': 1, 'name': 'Kiruna', 'latitude': 67.8500000, 'longitude': 20.2166667, 'altitude': 402.2, 'elevation': 8, 'bandwidth': 10e6, 'debit': 20e6, 'color': 'yellow' }
]

#Initialisation des missions (A SUPPRIMER QUAND L'INTERFACE SERA PRéSENTE !!)
Missions=[
    {'name': 'EO_Test', 'TI': 0, 'TF': 86400, 'TS': 100, 'sza_min': 60, 'depointing': False, 'type': 'EO' },
    {'name': 'SAR_Test', 'TI': 0, 'TF': 86400, 'TS': 100, 'sza_min': 0, 'depointing': True, 'type': 'SAR' }
]

#Definition des parametres de la mission
# Temps de simulation
TI = '2024-01-01 00:00:00'
TF = '2024-12-31 23:59:00'

t0 = 0 # Temps initial en s
tf = 86400 # Temps final en s
dt = 100  # Pas de temps en s

resolution_step = 10
sza_min = 60

#Definition de l'exportation

column_names = ["X", "Y", "Z", "Vx", "Vy", "Vz"]

