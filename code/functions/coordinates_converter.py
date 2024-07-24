from config import *
import numpy as np

def latlong_to_cartesian(lat, long, altitude):
    """
    Permet de passer de lat/long en cartesien ECEF.
    """
    #Reference : WGS84 ellipsoid --> goal : x,y,z in ECEF Frame
    a = earth_radius
    f = 1/298.257223563
    b= a*(1-f)
    e2 = 1-((b**2)/(a**2))
    N= a/np.sqrt(1-e2*(np.sin(np.deg2rad(lat)))**2)

    X = (N+altitude)*np.cos(np.deg2rad(lat))*np.cos(np.deg2rad(long))
    Y = (N+altitude)*np.cos(np.deg2rad(lat))*np.sin(np.deg2rad(long))
    Z = ((1-e2)*N+altitude)*np.sin(np.deg2rad(lat))
    
    return X, Y, Z

def ECEF_to_ENU(x, y, z, lat, lon, x_s, y_s, z_s):
    """
    Permet de passer de cartesien ECEF en cartesien ENU.
    """
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


def eci_to_ecef(sx, sy, sz, vx, vy, vz, t, theta0=0):
    """
    Transforme le vecteur d'état de ECI à ECEF.
    """
    theta = theta0 + omega_earth * t
    # Matrice de transformation ECI vers ECEF
    R = np.array([[np.cos(theta), np.sin(theta), 0],
                  [-np.sin(theta), np.cos(theta), 0],
                  [0, 0, 1]])
    
    r_eci = np.array([sx, sy, sz])
    v_eci = np.array([vx, vy, vz])

    r_ecef = R @ r_eci
    v_ecef = R @ v_eci + np.cross([0, 0, omega_earth], r_ecef)
    
    return np.concatenate((r_ecef, v_ecef))