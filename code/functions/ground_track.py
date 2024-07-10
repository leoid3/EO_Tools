import numpy as np
from functions.eci_to_ecef import eci_to_ecef
from config import *

def plot_ground_track(sat, times, ax, color, map):
    """
    Visualise la trace au sol de l'orbite du satellite.
    """
    lats = []
    lons = []
    marker_list = []
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
        marker = map.set_marker(lats[i], lons[i])
        marker_list.append(marker.position)
        marker.delete()
        if abs(lons[i+1] - lons[i]) > 180:
            segments.append((segment_lats, segment_lons))
            if len(marker_list) >=2:
                path = map.set_path(marker_list, color=sat.get_color(), width="1")
            marker_list=[]
            segment_lats = []
            segment_lons = []
            
        
    segment_lats.append(lats[-1])
    segment_lons.append(lons[-1])
    segments.append((segment_lats, segment_lons))
    marker = map.set_marker(lats[-1], lons[-1])
    marker_list.append(marker.position)
    marker.delete()
    path = map.set_path(marker_list, color=sat.get_color(), width="1")
    label = 'Ground Track of '+str(sat.get_name())
    
    for segment_lats, segment_lons in segments:
        ax.plot(segment_lons, segment_lats, label=label, color=color)
        label = None
    ax.plot(segment_lons[len(segment_lons)-1], segment_lats[len(segment_lats)-1], '*', label='Satellite ' +str(sat.get_name()), color=sat.get_color())
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Satellite Ground Track')
    ax.legend()

def show_gs_on_ground_track(gs, ax):
    ax.plot(gs.get_coordinate()[1], gs.get_coordinate()[0], 'o', label=gs.get_name(), color=gs.get_color())
    ax.legend()

def show_poi_on_ground_track(poi, ax):
    ax.plot(poi.get_coordinate(0)[1], poi.get_coordinate(0)[0], 'x', label=poi.get_name(), color=poi.get_color())
    ax.legend()