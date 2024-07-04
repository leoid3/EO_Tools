from config import *

def plot_orbit_3d(sat, ax, name, color):
    """
    Visualise l'orbite en 3D.
    """
    x, y, z = sat.get_position()

    ax.plot(x/1000, y/1000, z/1000, label='Constellation '+str(name), color=color)
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('Satellite Orbit in 3D')
    ax.legend()


def show_sat(sat, ax):
    """
    Affiche les satellites sur l'orbite.
    """ 
    x_sat, y_sat, z_sat = sat.get_position()

    ax.plot(x_sat[len(x_sat)-1]/1000, y_sat[len(y_sat)-1]/1000, z_sat[len(z_sat)-1]/1000, '*', label=f'Satellite {sat.get_name()}',color=sat.get_color(), markersize=6)
