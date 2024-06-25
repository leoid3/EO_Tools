import csv
from config import *

def export_to_csv(states, satID, constID, planID):
    """
    Exporte les positions et les vitesses du satellite.
    """
    file_name = f"Satellite {constID}-{satID+1} in plan {planID+1}.csv"

    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(states)
    return 