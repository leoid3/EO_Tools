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

#Definition de l'exportation

column_names = ["X", "Y", "Z", "Vx", "Vy", "Vz"]
list_colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
sat_type = ['SAR', 'EO']

