import numpy as np
from config import *

def eci_to_ecef(state, t, theta0=0):
    """
    Transforme le vecteur d'état de ECI à ECEF.
    """
    theta = theta0 + omega_earth * t
    R = np.array([[np.cos(theta), np.sin(theta), 0],
                  [-np.sin(theta), np.cos(theta), 0],
                  [0, 0, 1]])
    
    r_eci = state[:3]
    v_eci = state[3:]
    
    r_ecef = R @ r_eci
    v_ecef = R @ v_eci + np.cross([0, 0, omega_earth], r_ecef)
    
    return np.concatenate((r_ecef, v_ecef))