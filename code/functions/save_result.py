import csv
from config import *

def save_gs_visibility(result):
    resultfields =['Satellite name', 'Ground Station name', 'Begin', 'End']
    filename = f"Result_Ground Station visibility.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(resultfields)
        csvwriter.writerows(result)