from config import *
import itur #https://github.com/inigodelportillo/ITU-Rpy
#source : https://www.nasa.gov/smallsat-institute/sst-soa/soa-communications/#9.2

def get_attenuation(ele, band, lat, long, ant):
    match band:
        case 'VHF':
            f = 0.2*itur.u.GHz
        case 'UHF':
            f = 0.7*itur.u.GHz
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
        case 'K':
            f = 22.5* itur.u.GHz
        case 'Ka':
            f = 33* itur.u.GHz
        case 'V':
            f = 57* itur.u.GHz
        case _:
            f = 5* itur.u.GHz
    
    p=0.1
    d = ant* itur.u.m
    att_dB = itur.atmospheric_attenuation_slant_path(lat, long, f, ele, p, d)

    attenuation = 1-10**(-att_dB.value/10)
    return attenuation