import csv
from config import *

def save_gs_visibility(result):
    resultfields =['Satellite name', 'Ground Station name', 'Begin', 'End']
    filename = f"Result_Ground Station visibility ({result[0][0]}).csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(resultfields)
        csvwriter.writerows(result)

def save_poi_visibility(result):
    resultfields =[f'Satellite name', 'POI name', 'Begin', 'End']
    filename = f"Result_POI visibility ({result[0][0]}).csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(resultfields)
        csvwriter.writerows(result)