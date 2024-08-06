import geopandas as gpd
from pathlib import Path

#Constantes
G = 6.67430e-11  # Constante gravitationnelle en m^3 kg^-1 s^-2
M = 5.972e24  # Masse de la Terre en kg
mu = G * M  # Paramètre gravitationnel standard pour la Terre en m^3.s^-2
earth_radius = 6378e3 #rayon de la Terre en m
omega_earth = 7.2921159e-5 #vitesse de rotation de la Terre en rad.s^-1

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
gs_fields =['name', 'coordinate', 'altitude', 'elevation', 'bandwidth', 'debit', 'color']
cons_fields =['name', 'walkerT', 'walkerP', 'walkerF', 'satmodel', 'color']
sat_fields =['name', 'swath', 'depointing', 'type', 'color', 'orbit']

#Definition de l'exportation (résultats de simulation)
result_folder = Path("results/")
resultfields_gs =['Satellite name', 'Ground Station name', 'Start time (UTC)', 'Stop time (UTC)', 'Duration (s)']
resultfields_poi =[f'Satellite name', 'POI name', 'Start time (UTC)', 'Stop time (UTC)', 'Duration (s)']

#Listes pour l'IHM
list_colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
sat_type = ['SAR', 'EO']

