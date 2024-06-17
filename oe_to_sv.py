import numpy as np
from config import *


def orbital_elements_to_state_vectors(a, e, i, Ω, ω, ν):
    """
    Convertit les éléments orbitaux en vecteurs d'état (position et vitesse).
    """
    # Convertir les angles en radians
    i = np.radians(i)
    Ω = np.radians(Ω)
    ω = np.radians(ω)
    ν = np.radians(ν)

    # Paramètre du semi-latus rectum
    p = a * (1 - e**2)

    # Position dans le plan orbital
    r = p / (1 + e * np.cos(ν))
    x_orbital = r * np.cos(ν)
    y_orbital = r * np.sin(ν)

    # Vitesse dans le plan orbital
    h = np.sqrt(mu * p)
    vx_orbital = -np.sqrt(mu / p) * np.sin(ν)
    vy_orbital = np.sqrt(mu / p) * (e + np.cos(ν))

    # Matrice de rotation
    R1 = np.array([[np.cos(Ω), -np.sin(Ω), 0],
                   [np.sin(Ω), np.cos(Ω), 0],
                   [0, 0, 1]])

    R2 = np.array([[1, 0, 0],
                   [0, np.cos(i), -np.sin(i)],
                   [0, np.sin(i), np.cos(i)]])

    R3 = np.array([[np.cos(ω), -np.sin(ω), 0],
                   [np.sin(ω), np.cos(ω), 0],
                   [0, 0, 1]])

    R = R1 @ R2 @ R3

    # Vecteurs position et vitesse dans le plan inertiel
    position_orbital = np.array([x_orbital, y_orbital, 0])
    velocity_orbital = np.array([vx_orbital, vy_orbital, 0])

    position_inertial = R @ position_orbital
    velocity_inertial = R @ velocity_orbital

    return position_inertial, velocity_inertial