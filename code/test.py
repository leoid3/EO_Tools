"""
from astropy.coordinates import AltAz, EarthLocation
from astropy.time import Time
from astropy import units as u
from matplotlib.ticker import AutoLocator

from satmad.core.celestial_bodies_lib import EARTH
from satmad.propagation.classical_orb_elems import OsculatingKeplerianOrbElems
from satmad.propagation.numerical_propagators import NumericalPropagator
from satmad.utils.timeinterval import TimeInterval

from astropy.visualization import time_support, quantity_support
from matplotlib import pyplot as plt
from satmad.utils.discrete_time_events import DiscreteTimeEvents

time = Time("2020-01-01T11:30:00", scale="utc")
central_body = EARTH

# Initialise a near-polar orbit
sm_axis = 7191.9 * u.km
ecc = 0.02 * u.dimensionless_unscaled
incl = 98.0 * u.deg
raan = 306.6 * u.deg
arg_perigee = 314.1 * u.deg
true_an = 100.3 * u.deg

orb_elems = OsculatingKeplerianOrbElems(
    time, sm_axis, ecc, incl, raan, arg_perigee, true_an, central_body
)

# convert to cartesian coordinates - this is the initial condition for the propagation
pvt0 = orb_elems.to_cartesian()

# Set up propagation config
stepsize = 30 * u.s

prop_start = pvt0.obstime
prop_duration = 1.0 * u.day

# init propagator with defaults
# run propagation and get trajectory
trajectory = NumericalPropagator(stepsize).gen_trajectory(pvt0, TimeInterval(prop_start, prop_duration))

print(trajectory)

# Init ground location
gnd_loc = EarthLocation.from_geodetic(28.979530 * u.deg, 41.015137 * u.deg,  0 * u.m)

# Init the frames for each time
alt_az_frames = AltAz(location=gnd_loc, obstime=trajectory.coord_list.obstime)

# Generate the sat coords in Alt Az
alt_az_list = trajectory.coord_list.transform_to(alt_az_frames)

print(alt_az_list)



quantity_support()
time_support(format='isot')

time_list = trajectory.coord_list.obstime
el_list = alt_az_list.alt.deg

fig1, ax1 = plt.subplots(figsize=(12,8), dpi=100)

# Format axes - Change major ticks and turn grid on
ax1.xaxis.set_major_locator(AutoLocator())
ax1.yaxis.set_major_locator(AutoLocator())

ax1.grid(True)

# Set axis labels
ax1.set_ylabel("Elevation (deg)")

# Rotate x axis labels
ax1.tick_params(axis="x", labelrotation=90)

# plot the data and show the plot
ax1.plot(time_list, el_list)

plt.show()



# Find intervals in data
events = DiscreteTimeEvents(time_list, el_list, 5, neg_to_pos_is_start=True)

print("Start-End Intervals:")
print(events.start_end_intervals)

print("Max Elevation Times:")
print(events.max_min_table)
"""
import numpy as np

def ecef_coordinates(lat, lon, alt):
    # Constantes WGS84
    a = 6378137.0  # Rayon équatorial en mètres
    f = 1 / 298.257223563  # Aplatissement
    b = a * (1 - f)  # Rayon polaire en mètres
    e2 = 1 - (b**2 / a**2)  # Excentricité au carré

    # Convertir la latitude et la longitude en radians
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)

    # Calculer N(φ)
    N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)

    # Calculer les coordonnées ECEF
    X = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad)
    Y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad)
    Z = ((1 - e2) * N + alt) * np.sin(lat_rad)

    return X, Y, Z

def ecef_to_enu(x, y, z, lat, lon, x_s, y_s, z_s):
    # Convertir la latitude et la longitude de la station au sol en radians
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)
    
    # Matrice de transformation ECEF vers ENU
    transform_matrix = np.array([
        [-np.sin(lon_rad), np.cos(lon_rad), 0],
        [-np.sin(lat_rad) * np.cos(lon_rad), -np.sin(lat_rad) * np.sin(lon_rad), np.cos(lat_rad)],
        [np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)]
    ])
    
    # Vecteur de la station au satellite en ECEF
    ecef_vector = np.array([x - x_s, y - y_s, z - z_s])
    
    # Conversion en ENU
    enu_vector = transform_matrix @ ecef_vector
    return enu_vector

# Coordonnées de la station au sol
lat_station = 48.8584  # Latitude en degrés
lon_station = 2.2945   # Longitude en degrés
alt_station = 35       # Altitude en mètres

# Convertir la position de la station au sol en ECEF
X_s, Y_s, Z_s = ecef_coordinates(lat_station, lon_station, alt_station)

# Coordonnées du satellite en ECEF (exemple)
X_sat = 15600e3
Y_sat = 7540e3
Z_sat = 20140e3

# Conversion des coordonnées du satellite en ENU
enu_vector = ecef_to_enu(X_sat, Y_sat, Z_sat, lat_station, lon_station, X_s, Y_s, Z_s)

# Calcul de l'angle d'élévation
E, N, U = enu_vector
elevation_angle = np.arcsin(U / np.sqrt(E**2 + N**2 + U**2)) * (180 / np.pi)

print(f"Angle d'élévation : {elevation_angle:.2f} degrés")

# Vérification de la visibilité
if elevation_angle > 0:
    print("Le satellite est visible.")
else:
    print("Le satellite n'est pas visible.")
