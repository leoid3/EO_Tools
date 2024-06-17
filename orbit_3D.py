from config import *

def plot_orbit_3d(states, ax, i, color):
    """
    Visualise l'orbite en 3D.
    """
    x = states[:, 0]/1000
    y = states[:, 1]/1000
    z = states[:, 2]/1000

    ax.plot(x, y, z, label=f'Constellation {i}', color=color)
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('Satellite Orbit in 3D')
    ax.legend()


def show_sat(states, ax, i, j, color): 
    x_sat = states[:, 0]/1000
    y_sat = states[:, 1]/1000
    z_sat = states[:, 2]/1000

    ax.plot(x_sat[len(x_sat)-1], y_sat[len(y_sat)-1], z_sat[len(z_sat)-1], '*', label=f'Satellite {i+1}-{j}',color=color, markersize=6)
