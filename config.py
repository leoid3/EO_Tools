#Constantes
G = 6.67430e-11  # Constante gravitationnelle en m^3 kg^-1 s^-2
M = 5.972e24  # Masse de la Terre en kg
mu = G * M  # Paramètre gravitationnel standard pour la Terre en m^3.s^-2
earth_radius = 6378e3 #rayon de la Terre en m
omega_earth = 7.2921159e-5 #vitesse de rotation de la Terre en rad.s^-1


# Definition des constellations
constellation = [
    {'ID': 1, 'a': earth_radius + 618e3, 'e': 0.001, 'i': 98.567, 'Ω': 0, 'ω': 0, 'ν': 0, 'swath_width': 20e3, 'depointing': 45, 'color': 'green', 'type': 'EO', 'nb_sat': 5, 'nb_plan': 1},
      {'ID': 2, 'a': earth_radius + 20000e3, 'e': 0.001, 'i': 20, 'Ω': 0, 'ω': 0, 'ν': 0, 'swath_width': 290e3, 'depointing': 0, 'color': 'red', 'type': 'SAR', 'nb_sat': 20, 'nb_plan': 1}      
]
#Definition des points d'interets
Point_of_interest =[
    {'ID': 1, 'latitude': 43.60444444 , 'longitude':1.44388889, 'altitude': 150, 'timezone':'Etc/GMT+1', 'name': 'Toulouse', 'color':'red'},
    {'ID': 2, 'latitude': 65 , 'longitude':166, 'altitude': 20, 'timezone':'Etc/GMT+1', 'name': 'TEST', 'color':'black'}
]
#Definition des stations sol
Ground_station =[]

#Definition des parametres de la mission
# Temps de simulation
TI = '2024-01-01 00:00:00'
TF = '2024-12-31 23:59:00'

t0 = 0 # Temps initial en s
tf = 12000 # Temps final en s
dt = 10  # Pas de temps en s

resolution_step = 10
sza_min = 60