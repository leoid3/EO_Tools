import numpy as np
from functions.eci_to_ecef import eci_to_ecef
from config import *

def plot_ground_track(sat, times, ax, color):
    """
    Visualise la trace au sol de l'orbite du satellite.
    """
    lats = []
    lons = []
    
    x_sat, y_sat, z_sat = sat.get_position()
    vx_sat, vy_sat, vz_sat = sat.get_velocity()

    for sx, sy, sz, vx, vy, vz, t in zip(x_sat, y_sat, z_sat, vx_sat, vy_sat, vz_sat, times):
        state_ecef = eci_to_ecef(sx, sy, sz, vx, vy, vz, t)
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
    
    label = 'Ground Track of '+str(sat.get_name())
    
    for segment_lats, segment_lons in segments:
        ax.plot(segment_lons, segment_lats, label=label, color=color)
        label = None
    ax.plot(segment_lons[len(segment_lons)-1], segment_lats[len(segment_lats)-1], '*', label='Satellite ' +str(sat.get_name()), color=color)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Satellite Ground Track')
    ax.legend()
    
    """
    temp_lat = []
    temp_long = []

    for i in range(len(segment_lats)):
        temp_lat.append(segment_lats[i])
    for j in range(len(segment_lons)):
        temp_long.append(segment_lons[j])
    markerini = map.set_marker(segment_lats[0], segment_lons[0])
    for k in range(len(temp_lat)):
        if k == 0: 
            marker1 = markerini
        else:
            marker1 = map.set_marker(segment_lats[k-1], segment_lons[k-1])
        marker2 = map.set_marker(segment_lats[k], segment_lons[k])   
        path = map.set_path([marker1.position, marker2.position])
        marker1.delete()
        marker2.delete()
    """