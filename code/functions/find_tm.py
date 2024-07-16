from classes.poi import Point_of_interest
import timezonefinder as tz
import pytz
import datetime
from config import *

def findtimezone(coord):
    """
    Permet de trouver la timezone liée a la latitude et longitude.
    """
    tf = tz.TimezoneFinder()
    timezone_str = tf.certain_timezone_at(lat = coord[1], lng =coord[0])
    if timezone_str is None:
        print("Impossible de trouver la zone temporelle du point, valeur par defaut: Etc/GMT+1")
        tm = 'Etc/GMT+1'
    else:
        poitz = pytz.timezone(timezone_str)
        dt = datetime.datetime.utcnow()
        print(str(poitz))
        utcoffset = poitz.localize(dt).strftime('%z')
        if (int(utcoffset[1:3]) < 10) and (int(utcoffset[1:3]) > -10):
            tm = 'Etc/GMT'+str(utcoffset[0])+str(utcoffset[2])
        else: 
            tm = 'Etc/GMT'+str(utcoffset[0:3])
        print(tm)
    return tm

def centroid(coord):
    """
    Permet de trouver le centre d'un polygone.
    """
    vertices = []
    for i in range(len(coord)):
        if len(coord[i])>2:
            for j in range(len(coord[i])):
                temp = coord[i][j]
                lat = temp[0]
                long = temp[1]
                vertices.append((long, lat))
        else:
            lat = coord[i][0]
            long = coord[i][1]
            vertices.append((long, lat))
    x, y = 0, 0
    n = len(vertices)
    signed_area = 0
    for i in range(len(vertices)):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        # shoelace formula
        area = (x0 * y1) - (x1 * y0)
        signed_area += area
        x += (x0 + x1) * area
        y += (y0 + y1) * area
    signed_area *= 0.5
    x /= 6 * signed_area
    y /= 6 * signed_area
    print(x, y)
    return x, y