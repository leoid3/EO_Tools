from config import *
import itur

def get_attenuation(ele, band, lat, long):
    match band:
        case 'L':
            f = 1.5* itur.u.GHz
        case 'S':
            f = 3* itur.u.GHz
        case 'C':
            f = 6* itur.u.GHz
        case 'X':
            f= 10* itur.u.GHz
        case 'Ku':
            f = 15* itur.u.GHz
        case 'Ka':
            f = 33* itur.u.GHz
        case _:
            f = 5* itur.u.GHz
    
    p=0.1
    d = antenna_dia* itur.u.m
    att_dB = itur.atmospheric_attenuation_slant_path(lat, long, f, ele, p, d)

    attenuation = 1-10**(-att_dB.value/10)
    return attenuation