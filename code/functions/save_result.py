import csv
from config import *

def save_gs_visibility(result):
    filename = result_folder / f"Result_Ground Station visibility ({result[0][0]}).csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(resultfields_gs)
        csvwriter.writerows(result)

def save_poi_visibility(result):
    filename = result_folder / f"Result_POI visibility ({result[0][0]}).csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(resultfields_poi)
        csvwriter.writerows(result)