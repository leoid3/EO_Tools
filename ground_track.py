import numpy as np
from eci_to_ecef import eci_to_ecef
from config import *

def plot_ground_track(states, times, ax, j, l, color):
    """
    Visualise la trace au sol de l'orbite du satellite.
    """
    lats = []
    lons = []
    for state, t in zip(states, times):
        state_ecef = eci_to_ecef(state, t)
        x, y, z = state_ecef[:3]
        lat = np.degrees(np.arcsin(z / np.linalg.norm([x, y, z])))
        lon = np.degrees(np.arctan2(y, x))
        lats.append(lat)
        lons.append(lon)
    
    # Séparer les segments de la trace au sol
    segments = []
    segment_lats = []
    segment_lons = []
    for i in range(len(lons) - 1):
        segment_lats.append(lats[i])
        segment_lons.append(lons[i])
        if abs(lons[i+1] - lons[i]) > 180:
            segments.append((segment_lats, segment_lons))
            segment_lats = []
            segment_lons = []
    segment_lats.append(lats[-1])
    segment_lons.append(lons[-1])
    segments.append((segment_lats, segment_lons))
    
    label = f'Ground Track {j}'

    for segment_lats, segment_lons in segments:
        ax.plot(segment_lons, segment_lats, label=label, color=color)
        label = None
    ax.plot(segment_lons[len(segment_lons)-1], segment_lats[len(segment_lats)-1], '*', label=f'Satellite {l+1}-{j}', color=color)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Satellite Ground Track')
    ax.legend()

