import numpy as np
from config import *

def eci_to_ecef(sx, sy, sz, vx, vy, vz, t, theta0=0):
    """
    Transforme le vecteur d'état de ECI à ECEF.
    """
    theta = theta0 + omega_earth * t
    R = np.array([[np.cos(theta), np.sin(theta), 0],
                  [-np.sin(theta), np.cos(theta), 0],
                  [0, 0, 1]])
    
    r_eci = np.array([sx, sy, sz])
    v_eci = np.array([vx, vy, vz])

    r_ecef = R @ r_eci
    v_ecef = R @ v_eci + np.cross([0, 0, omega_earth], r_ecef)
    
    return np.concatenate((r_ecef, v_ecef))