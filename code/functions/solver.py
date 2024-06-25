import numpy as np
from config import *

def deriv(t, state):
    """
    Calcule les dérivées du vecteur état [x, y, z, vx, vy, vz].
    """
    x, y, z, vx, vy, vz = state
    r = np.sqrt(x**2 + y**2 + z**2)
    
    ax = -mu * x / r**3
    ay = -mu * y / r**3
    az = -mu * z / r**3
    
    return np.array([vx, vy, vz, ax, ay, az])

def runge_kutta_4(deriv, state0, t0, tf, dt):
    """
    Intégrateur de Runge-Kutta d'ordre 4 pour résoudre le problème de gravitation
    """
    t = t0
    state = state0
    states = [state0]
    times = [t0]
    
    while t < tf:
        k1 = dt * deriv(t, state)
        k2 = dt * deriv(t + 0.5 * dt, state + 0.5 * k1)
        k3 = dt * deriv(t + 0.5 * dt, state + 0.5 * k2)
        k4 = dt * deriv(t + dt, state + k3)
        
        state = state + (k1 + 2*k2 + 2*k3 + k4) / 6.0
        t += dt
        
        states.append(state)
        times.append(t)
    
    return np.array(times), np.array(states)