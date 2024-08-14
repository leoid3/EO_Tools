import csv
from config import *
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import matplotlib.pyplot as plt
import numpy as np
import io
from functions.calcul import simulation_time
from functions.find_tm import centroid

def save_gs_visibility(result):
    if len(result) == 0:
        print("NO OPPORTUNITIES")
    else:
        filename = result_folder / f"Result Ground Station visibility ({result[0][0]}).csv"
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(resultfields_gs)
            csvwriter.writerows(result)

def save_poi_visibility(result):
    if len(result) == 0:
        print("NO OPPORTUNITIES")
    else:
        filename = result_folder / f"Result POI visibility ({result[0][0]}).csv"
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(resultfields_poi)
            csvwriter.writerows(result)

def general_result(mission):
    ##### Mission
    missionname = mission.get_name()
    missiontype = mission.get_type()
    delta, _, _, _ = simulation_time(mission)
    if delta.days == 0:
        missionduration = 1
    else:
        missionduration = delta.days
    missionsza = mission.get_minsza()
    poi = []
    for i in range(mission.get_nb_poi()):
        poi.append(mission.get_poi(i))
    gs = []
    for i in range(mission.get_nb_gs()):
        gs.append(mission.get_gs(i))
    missionconst = mission.get_constellation()

    ##### Constellation
    constname = missionconst.get_name()
    numbersat = missionconst.get_walkerT()
    numberplane = missionconst.get_walkerP()
    phasing = missionconst.get_walkerF()
    satmodel = missionconst.get_model()
    satmodel_name = satmodel.get_name()
    orbit = satmodel.get_orbit()
    a, e, incl, _, _, _ = orbit.get_all()
    if ((a-earth_radius)/1000>0) and ((a-earth_radius)/1000<=2000):
        orbittype = "LEO"
    elif  ((a-earth_radius)/1000>2000) and ((a-earth_radius)/1000<35786):
        orbittype = "MEO"
    elif (a-earth_radius)/1000==35786:
        orbittype = "GEO"
    else:
        orbittype = "Undefined"
    semimajoraxis = a/1000
    inclination = incl
    eccentricity = e
    period = 2*np.pi*np.sqrt((a**3)/mu)
    numberorbit = 86400/period
    revisit0 = "XX"
    revisit45="XX"
    revisit60="XX"
    swath = satmodel.get_swath()
    depointing = satmodel.get_depoiting()

    ##### POI
    listpoi = []
    listpoi.append("liste")
    for i in range(mission.get_nb_poi()):
        listpoi.append(mission.get_poi(i))

    ##### GS
    listegs = []
    listegs.append("liste")
    for i in range(mission.get_nb_gs()):
        listegs.append(mission.get_gs(i))

    doc = Document("Mission report Template.docx")
    text_elements = []
    for para in doc.paragraphs:
        text_elements.append(para.text)

    # Function to replace XX with actual values
    def replace_placeholders(text, values):
        for key, value in values.items():
            if value== poi:
                new_value =''
                for i in range(len(value)):
                    if i==0:
                        temp = value[i]
                        new_value ="- " + temp.get_name()
                    else:
                        temp = value[i]
                        new_value =new_value + "<br></br>" + "- "+ temp.get_name()
                text = text.replace(key, new_value)
            elif value== gs:
                new_value =''
                for i in range(len(value)):
                    if i==0:
                        temp = value[i]
                        new_value ="- " + temp.get_name()
                    else:
                        temp = value[i]
                        new_value =new_value + "<br></br>" + "- "+ temp.get_name()
                text = text.replace(key, new_value)
            elif value== listpoi:
                new_value =''
                for i in range(len(value)):
                    temp = value[i]
                    if i==0:
                        pass
                    else:
                        if temp.IsArea() == True:
                            long, lat = centroid(temp.get_area())
                        else:
                            lat = temp.get_coordinate(0)[0]
                            long = temp.get_coordinate(0)[1]
                        if i == 1:
                            new_value = temp.get_name() + "<br></br>" + "Coordinates : " + str(lat) + "°  " + str(long) + "°" + "<br></br>" + "Altitude : " + str(temp.get_altitude()) + " m" + "<br></br>" + "Total number of times visible : " + "XX" + "<br></br>" + "Mean duration time : " + "XX" +" s" + "<br></br>"
                        else:
                            new_value = new_value + "<br></br>" + "Name of the point of interest : " + temp.get_name() + "<br></br>" + "Coordinates : " + str(lat) + "°  " + str(long) + "°" + "<br></br>" + "Altitude : " + str(temp.get_altitude()) + " m" + "<br></br>" + "Total number of times visible : " + "XX" + "<br></br>" + "Mean duration time : " + "XX" +" s" + "<br></br>"
                text = text.replace(key, new_value)
            elif value == listegs:
                new_value =''
                for i in range(len(value)):
                    temp = value[i]
                    if i== 0:
                        pass
                    else:
                        lat, long = temp.get_coordinate()
                        if i == 1:
                            new_value = temp.get_name() + "<br></br>" + "Coordinates : " + str(lat) + "°  " + str(long) + "°" + "<br></br>" + "Altitude : " + str(temp.get_altitude()) + " m" + "<br></br>" + "Antenna characteristics :" + "<br></br>" + "- Elevation : " + str(temp.get_elevation()) + " °" + "<br></br>" + "- Band : " + temp.get_band() + "<br></br>" + "- Debit : " + str(temp.get_debit()) + " Mbps" + "<br></br>" + "Total number of opportunities : " + "XX" + "<br></br>" + "Mean duration time : " + "XX" + " s" + "<br></br>" + "Mean data size send/received : " + "XX" + " Mb" + "<br></br>"
                        else:
                            new_value = new_value + "<br></br>" + "Name of the ground station : " + temp.get_name() + "<br></br>" + "Coordinates : " + str(lat) + "°  " + str(long) + "°" + "<br></br>" + "Altitude : " + str(temp.get_altitude()) + " m" + "<br></br>" + "Antenna characteristics :" + "<br></br>" + "- Elevation : " + str(temp.get_elevation()) + " °" + "<br></br>" + "- Band : " + temp.get_band() + "<br></br>" + "- Debit : " + str(temp.get_debit()) + " Mbps" + "<br></br>" + "Total number of opportunities : " + "XX" + "<br></br>" + "Mean duration time : " + "XX" + " s" + "<br></br>" + "Mean data size send/received : " + "XX" + " Mb" + "<br></br>"
                text = text.replace(key, new_value)
            else:
                text = text.replace(key, value)
        return text

    # Define specific keywords that indicate where plots should be inserted
    plot_keywords = [
        "Map with GS & POI",
        "3D orbit",
        "Ground track",
    ]

    plot_images = {
        "Map with GS & POI" : result_folder / f"Ground Track of {missionname}.png",
        "3D orbit" : result_folder / f"Orbit of {missionname}.png",
        "Ground track" : result_folder / f"Ground Track of {missionname}.png",
    }

    # Define specific keywords that indicate titles and sections
    main_title = ["Mission report"]
    secondary_title = [
        "Mission details",
        "Constellation details",
        "Point of interest details",
        "Ground Station details"
    ]

    # Define the values to replace
    values = {
        
        "<MissionName>": missionname,
        "<MissionType>": missiontype,
        "<MissionDuration>": str(missionduration),
        "<MissionSZA>": str(missionsza),
        "<POIName> (<Latitude> <Longitude>)": poi,
        "<GSName> (<Latitude> <Longitude>)": gs,
        "<MissionConstellation>": constname,
        "<ConstellationName>": constname,
        "<NumberofSat>": str(numbersat), 
        "<NumberofPlane>": str(numberplane), 
        "<PhasingFactor>": str(phasing), 
        "<SatName>": satmodel_name, 
        "<Typeoforbit>": orbittype, 
        "<semimajoraxis>": str(semimajoraxis), 
        "<inclination>": str(inclination), 
        "<eccentricity>": str(eccentricity), 
        "<period>": str(period), 
        "<Numberoforbit>": str(numberorbit), 
        "<revisitat0>": str(revisit0), 
        "<revisitat45>": str(revisit45), 
        "<revisitat60>": str(revisit60), 
        "<swath>": str(swath), 
        "<depointing>": str(depointing),
        "<POIStart>": listpoi,
        "<GSStart>": listegs,   
        "XX" : "PLACEHOLDER",
    }

    # Create a custom style for titles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='secondarytitle', fontSize=16, leading=16, bold=True))
    styles.add(ParagraphStyle(name='maintitle',fontSize=28, leading=16, alignment=TA_CENTER, spaceAfter=12, bold=True))
    styles.add(ParagraphStyle(name='body',fontSize=12, leading=16))

    # Create the PDF document with enhanced formatting
    pdf_filename = "Mission Report.pdf"
    pdf = SimpleDocTemplate(pdf_filename, pagesize=A4)

    elements = []

    for text in text_elements:
        # Replace placeholders
        formatted_text = replace_placeholders(text, values)
        
        # Check if the text matches any of the keywords that indicate a title
        if any(keyword in formatted_text for keyword in main_title):
            elements.append(Paragraph(formatted_text, styles["maintitle"]))
        elif any(keyword in formatted_text for keyword in plot_keywords):
            for keyword, image_path in plot_images.items():
                if keyword in formatted_text:
                    if keyword == "3D orbit":
                        img = Image(image_path, width=400, height=300)
                    else:
                        img = Image(image_path, width=600, height=300)
                    elements.append(img)
                
        elif any(keyword in formatted_text for keyword in secondary_title):
            elements.append(PageBreak())
            elements.append(Paragraph(formatted_text, styles["secondarytitle"]))
        else:
            elements.append(Paragraph(formatted_text, styles["body"]))
        
        elements.append(Spacer(1, 12))

    # Build PDF
    pdf.build(elements)

    # Output the path to the generated PDF
    print(f"PDF created successfully: {pdf_filename}")

    

    