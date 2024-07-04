
import numpy as np
import matplotlib.pyplot as plt

def revisite():
    #Definition de l'orbite (supposée SSO et képlérienne donc i=98° et sans perturbation)
    h = 450 #en km
    R= 6378 #en km
    mu = 398600 #en km^3.s^-2
    T= 2*np.pi*np.sqrt((h+R)**3/mu) #période en s
    nb_orbit = 24/(T/3600)
    print("nombre d'orbites par jour : ", nb_orbit)

    #Definition du satellite
    nb_sat = 3
    swath = 25 #en km
    FOV = np.arctan((swath/2)/h) #en rad
    depointing = 45 #en deg
    depointing = depointing*np.pi/180 #en rad

    W = R*np.sin(np.arctan((h*np.tan(FOV + depointing))/R)) # fauchée en prenant en compte le dépointage
    
    #Calcul de la revisite
    lat= [0, 15, 30, 45, 60, 75, 89] #en deg
    peri = 2*np.pi*R
    #nb_revisit=(nb_sat*2*W*nb_orbit)/(peri*np.cos(lat))
    #print("nombre de revisite : ", nb_revisit, "avec ", nb_sat, " satellites")

    nb_revisit = np.zeros((len(lat), nb_sat))
    for i in range(len(lat)):
        for j in range(nb_sat):
            nb_revisit[i, j]= ((j+1)*2*W*nb_orbit)/(peri*np.cos(lat[i]*np.pi/180))
    print(nb_revisit)

    satellite = np.arange(nb_sat)
    for k in range(len(satellite)):
        satellite[k] += 1
    
    return

if __name__=='__main__':
    revisite()