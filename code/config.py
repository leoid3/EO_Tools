import geopandas as gpd
from pathlib import Path

#Constantes
G = 6.67430e-11  # Constante gravitationnelle en m^3 kg^-1 s^-2
M = 5.972e24  # Masse de la Terre en kg
mu = G * M  # Paramètre gravitationnel standard pour la Terre en m^3.s^-2
earth_radius = 6378e3 #rayon de la Terre en m
omega_earth = 7.2921159e-5 #vitesse de rotation de la Terre en rad.s^-1
com_prot = 0.15 #https://www.techniques-ingenieur.fr/base-documentaire/technologies-de-l-information-th9/techniques-et-systemes-de-transmission-en-reseaux-et-telecoms-42293210/systemes-de-communications-par-satellite-e7560/architecture-des-systemes-de-communication-par-satellite-e7560v3niv10001.html
error_correction = 0.1 #https://cours.zaretti.be/courses/coding/algo/lessons/controle-derreur-crc-parite-etc/?action=register
noise = 0.025 #https://cel.hal.science/cel-00156394/file/cours.pdf
eff_ini = (1-com_prot)*(1-error_correction)*(1-noise)

#Listes données
liste_satellite = []
liste_poi = []
liste_gs = []
liste_constellation = []
liste_mission = []

#sources maps
satellite_map = "https://mt1.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}"
normal_map ="https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga"

#Dataset
folder = Path("dataset/50/")
path_to_shapefile = folder / "ne_50m_admin_0_map_units.shp"
world = gpd.read_file(path_to_shapefile)

#Definition de l'exportation (données de simulation)
simulation_folder = Path("simulation_data/")
mission_fields = ['name', 'starttime', 'endtime', 'timestep', 'type', 'minsza', 'poi', 'gs', 'constellation']
poi_fields = ['name', 'coordinate', 'altitude','color', 'timezone', 'sza', 'area']
gs_fields =['name', 'coordinate', 'altitude', 'elevation','antenna', 'band', 'debit', 'color']
cons_fields =['name', 'walkerT', 'walkerP', 'walkerF', 'satmodel', 'color']
sat_fields =['name', 'swath', 'depointing', 'type', 'color', 'orbit']

#Definition de l'exportation (résultats de simulation)
result_folder = Path("results/")
resultfields_gs =['Satellite name', 'Ground Station name', 'Start time (UTC)', 'Stop time (UTC)', 'Duration (s)', 'Data received (Mb)']
resultfields_poi =[f'Satellite name', 'POI name', 'Start time (UTC)', 'Stop time (UTC)', 'Duration (s)', 'Mean solar elevation (°)']

#Listes pour l'IHM
list_colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
sat_type = ['SAR', 'EO']
list_bande = ['VHF', 'UHF', 'L', 'S', 'C', 'X', 'Ku','K', 'Ka', 'V']

