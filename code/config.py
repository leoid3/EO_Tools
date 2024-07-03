#Constantes
G = 6.67430e-11  # Constante gravitationnelle en m^3 kg^-1 s^-2
M = 5.972e24  # Masse de la Terre en kg
mu = G * M  # Paramètre gravitationnel standard pour la Terre en m^3.s^-2
earth_radius = 6378e3 #rayon de la Terre en m
omega_earth = 7.2921159e-5 #vitesse de rotation de la Terre en rad.s^-1

liste_satellite = []
liste_poi = []
liste_gs = []
liste_constellation = []
liste_mission = []

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
list_colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
sat_type = ['SAR', 'EO']

