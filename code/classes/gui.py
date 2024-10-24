import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename, askdirectory
import matplotlib
matplotlib.use("TkAgg")
import tkintermapview as tkmap
from satellite_tle import fetch_tle_from_celestrak
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from tkcalendar import DateEntry
import numpy as np
from datetime import timedelta, datetime
from shapely.geometry import Polygon, Point
import geopandas as gpd

from config import *
from functions.initialisation import init_constellation, init_poi, init_gs, init_mission, init_sat, init_orb, reset_liste
from functions.calcul import calcul_traj, true_anomaly, simulation_time, calcul_swath, gs_interval, poi_interval, poi_grid, partition, sun_zenith_angle
from functions.save_data import save_to_csv
from functions.import_data import import_from_csv, import_poi_csv, import_gs_csv
from functions.country import get_country_name, get_poly_coordinate
from functions.coordinates_converter import latlong_to_cartesian
from functions.save_result import save_gs_visibility, save_poi_visibility, general_result
from functions.itur_model import get_attenuation

#############################################################################################
# Main window

class SatelliteSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.marker_list=[]
        self.marker_poi = []
        self.poly_list = []
        self.country_coords =[]
        self.grid_coords = []
        self.grid_poly = []
        self.country_marker =[]
        self.calcul_marker =[]
        self.selected_country_coords = []
        self.final_poly_list = []
        self.satellite_marker =[]
        self.flag_area = False
        self.flag_country = False
        self.flag_mod_sat = False
        self.flag_mod_const = False
        self.flag_mod_gs = False
        self.flag_mod_poi = False
        self.title("EO Tools")
        self.geometry("1920x1080")

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.map_tab()
        self.tab1() #Onglet satellite + orbit
        self.tab2() #Onglet constellation
        self.tab3() #Onglet POI
        self.tab5() #Onglet Mission
        self.tab6() #Onglet resultats

    def map_tab(self):
        map_frame = ttk.LabelFrame(self.main_frame, text="Map")
        map_frame.place(relx = 0.48, rely= 0, anchor="n")
        self.__map_widget = tkmap.TkinterMapView(map_frame, width=700,
                                         height=700, corner_radius = 0)
        self.__map_widget.set_tile_server(normal_map, max_zoom=20)
        self.__map_widget.place(relx = 0.5, rely=0.5, anchor= tk.CENTER)
        self.__map_widget.set_position(48.860381, 2.338594)  # Paris, France
        self.__map_widget.set_zoom(3)
        self.__map_widget.pack()
        self.__map_widget.add_right_click_menu_command(label="Add POI", command=self.copy_coords_poi, pass_coords=True)
        self.__map_widget.add_right_click_menu_command(label="Add GS", command=self.copy_coords_gs, pass_coords=True)
        self.__map_widget.add_right_click_menu_command(label="Add Marker", command=self.add_marker_hand, pass_coords=True)
        self.__map_widget.add_right_click_menu_command(label="Select a Country", command=self.add_marker_country, pass_coords=True)
        
        self.comb_aff_sat = ttk.Combobox(map_frame, postcommand=self.comb_miss_simu)
        self.comb_aff_sat.pack(anchor="s")
        self.comb_aff_sat['state'] = 'readonly'
        self.comb_aff_sat.set('Choose a satellite...')
        self.comb_aff_sat.config(state='disable')
        ttk.Button(map_frame, text="Load", command=self.showsatonmap).pack(anchor="s")
        ttk.Button(map_frame, text="Save mission result", command=self.save_result).pack(side="right")

        ttk.Button(map_frame, text="Satellite view", command=self.set_map_satellite).pack(side= "left")
        ttk.Button(map_frame, text="Map view", command=self.set_map_default).pack(side="left")
        
    def set_map_satellite(self):
        self.__map_widget.set_tile_server(satellite_map, max_zoom=20)
    
    def set_map_default(self):
        self.__map_widget.set_tile_server(normal_map, max_zoom=20)

    def showsatonmap(self):
        index_path = 0
        self.__map_widget.delete_all_path()
        if len(self.satellite_marker) != 0:
            self.satellite_marker[0].delete()
            self.satellite_marker=[]

        for i in range(len(liste_mission)):
                if liste_mission[i].get_name()==str(self.combo_mission.get()):
                    miss = liste_mission[i]
                    cons = miss.get_constellation()
                    for j in range(int(cons.get_walkerT())):
                        sat = cons.get_sat(j)
                        if (sat.get_name()) == str(self.comb_aff_sat.get()):
                            index_path=j
                            chosen_sat = sat
        if chosen_sat == None:
            showinfo("Error", "Something went wrong")
        else:
            for i in range(len(self.calcul_marker[index_path])):
                if len(self.calcul_marker[index_path][i]) >=2:
                    path = self.__map_widget.set_path(self.calcul_marker[index_path][i], name=chosen_sat.get_name(), color=chosen_sat.get_color(), width="1")
            pos =self.calcul_marker[index_path][len(self.calcul_marker[index_path])-1]
            sat_pos = pos[-1]
            marker = self.__map_widget.set_marker(sat_pos[0], sat_pos[1], text=chosen_sat.get_name(), marker_color_outside=chosen_sat.get_color())
            self.satellite_marker.append(marker)
            window = ResultChoiceWindow(self.gs_visibility, self.poi_visibility, miss, chosen_sat)
                 
    def tab1(self):
        # Frame for the satellite tab
        self.sat_frame = ttk.LabelFrame(self.main_frame, text="Satellite Creation :", padding=(10, 10))
        self.sat_frame.place(relx= 0.1, rely=0, anchor= "n")

        self.l_sn = ttk.Label(self.sat_frame, text="Name of the Satellite : ")
        self.l_sn.grid(row=0, column=0, sticky="w")
        self.sat_name = ttk.Entry(self.sat_frame)
        self.sat_name.grid(row=0, column=1, sticky="e")

        self.l_sw = ttk.Label(self.sat_frame, text="Swath (km) : ")
        self.l_sw.grid(row=1, column=0, sticky="w")
        self.sat_swath = ttk.Entry(self.sat_frame)
        self.sat_swath.grid(row=1, column=1, sticky="e")

        self.l_dep = ttk.Label(self.sat_frame, text="Depointing (°) : ")
        self.l_dep.grid(row=2, column=0, sticky="w")
        self.sat_dep = ttk.Entry(self.sat_frame)
        self.sat_dep.grid(row=2, column=1, sticky="e")

        ttk.Label(self.sat_frame, text="Color : ").grid(row=3, column=0, sticky="w")
        self.combo_color = ttk.Combobox(self.sat_frame)
        self.combo_color.grid(row=3, column=1, sticky="e")
        self.combo_color['state'] = 'readonly'
        self.combo_color.set(list_colors[0])
        self.combo_color['values'] = list_colors
        

        ttk.Label(self.sat_frame, text="Type : ").grid(row=4, column=0, sticky="w")
        self.combo_type = ttk.Combobox(self.sat_frame)
        self.combo_type.grid(row=4, column=1, sticky="e")
        self.combo_type['state'] = 'readonly'
        self.combo_type.set(sat_type[0])
        self.combo_type['values'] = sat_type

        # Frame for the orbit
        ttk.Label(self.sat_frame, text='Orbit Creation :').grid(row=5, column=0, padx=10, pady=10, sticky="nw")
        self.l_a =ttk.Label(self.sat_frame, text="Altitude (km):")
        self.l_a.grid(row=6, column=0, sticky="w")
        self.altitude = ttk.Entry(self.sat_frame)
        self.altitude.grid(row=6, column=1, sticky="e")

        self.l_e = ttk.Label(self.sat_frame, text="Eccentricity:")
        self.l_e.grid(row=7, column=0, sticky="w")
        self.eccentricity = ttk.Entry(self.sat_frame)
        self.eccentricity.grid(row=7, column=1, sticky="e")

        self.l_i = ttk.Label(self.sat_frame, text="Inclination (°):")
        self.l_i.grid(row=8, column=0, sticky="w")
        self.inclination = ttk.Entry(self.sat_frame)
        self.inclination.grid(row=8, column=1, sticky="e")

        self.l_raan = ttk.Label(self.sat_frame, text="RAAN (°):")
        self.l_raan.grid(row=9, column=0, sticky="w")
        self.raan = ttk.Entry(self.sat_frame)
        self.raan.grid(row=9, column=1, sticky="e")

        self.l_ap = ttk.Label(self.sat_frame, text="Argument of Perigee (°):")
        self.l_ap.grid(row=10, column=0, sticky="w")
        self.arg_perigee = ttk.Entry(self.sat_frame)
        self.arg_perigee.grid(row=10, column=1, sticky="e")

        self.l_ta = ttk.Label(self.sat_frame, text="True Anomaly (°):")
        self.l_ta.grid(row=11, column=0, sticky="w")
        self.true_anomaly = ttk.Entry(self.sat_frame)
        self.true_anomaly.grid(row=11, column=1, sticky="e")

        ttk.Button(self.sat_frame, text="Add Satellite", command=self.add_satellite).grid(row=12, column=2, pady=10)
        ttk.Button(self.sat_frame, text="Modify Satellite", command=self.modify_satellite).grid(row=12, column=1, pady=10)
        ttk.Button(self.sat_frame, text="Delete Satellite", command=self.delete_satellite).grid(row=12, column=0, pady=10)
        ttk.Button(self.sat_frame, text="Import TLE", command=self.openTLEwindow).grid(row=13, column=1, pady=10)

    def tab2(self):
        self.const_frame = ttk.LabelFrame(self.main_frame, text="Constellation Creation :", padding=(10, 10))
        self.const_frame.place(relx= 0.117, rely=0.45, anchor= "n")

        self.l_consn = ttk.Label(self.const_frame, text="Name of the Constellation : ")
        self.l_consn.grid(row=0, column=0, sticky="w")
        self.const_name = ttk.Entry(self.const_frame)
        self.const_name.grid(row=0, column=1, sticky="e")

        ttk.Label(self.const_frame, text="Walker Constellation Parameters : ").grid(row=1, column=0, sticky="w")
        self.l_walkerT = ttk.Label(self.const_frame, text="Number of total Satellite : ")
        self.l_walkerT.grid(row=2, column=0, sticky="w")
        self.walkerT = ttk.Entry(self.const_frame)
        self.walkerT.grid(row=2, column=1, sticky="e")

        self.l_walkerP = ttk.Label(self.const_frame, text="Number of orbital plane : ")
        self.l_walkerP.grid(row=3, column=0, sticky="w")
        self.walkerP = ttk.Entry(self.const_frame)
        self.walkerP.grid(row=3, column=1, sticky="e")

        self.l_walkerF = ttk.Label(self.const_frame, text="Phasing factor : ")
        self.l_walkerF.grid(row=4, column=0, sticky="w")
        self.walkerF = ttk.Entry(self.const_frame)
        self.walkerF.grid(row=4, column=1, sticky="e")

        self.l_combo_sat =ttk.Label(self.const_frame, text="Choose a Satellite's model : ")
        self.l_combo_sat.grid(row=5, column=0, sticky="w")
        self.combo_sat = ttk.Combobox(self.const_frame, postcommand= self.comb_sat_upd)
        self.combo_sat.grid(row=5, column=1, sticky="e")
        self.combo_sat['state'] = 'readonly'
        self.combo_sat.set('Choose a model...')

        ttk.Label(self.const_frame, text="Color : ").grid(row=6, column=0, sticky="w")
        self.combo_color_const = ttk.Combobox(self.const_frame)
        self.combo_color_const.grid(row=6, column=1, sticky="e")
        self.combo_color_const['state'] = 'readonly'
        self.combo_color_const.set(list_colors[0])
        self.combo_color_const['values'] = list_colors

        ttk.Button(self.const_frame, text="Add Constellation", command=self.add_constellation).grid(row=7, column=2, pady=10)
        ttk.Button(self.const_frame, text="Modify Constellation", command=self.modify_constellation).grid(row=7, column=1, pady=10)
        ttk.Button(self.const_frame, text="Delete Constellation", command=self.delete_constellation).grid(row=7, column=0, pady=10)

    def tab3(self):
        self.poi_frame = ttk.LabelFrame(self.main_frame, text="Point of Interest Creation :", padding=(10, 10))
        self.poi_frame.place(relx= 0.73, rely=0)

        self.l_poin = ttk.Label(self.poi_frame, text="Name of the POI : ")
        self.l_poin.grid(row=0, column=0, sticky="w")
        self.poi_name = ttk.Entry(self.poi_frame)
        self.poi_name.grid(row=0, column=1, sticky="e")

        self.l_lat = ttk.Label(self.poi_frame, text="Latitude (DD) : ")
        self.l_lat.grid(row=1, column=0, sticky="w")
        self.poi_lat = ttk.Entry(self.poi_frame)
        self.poi_lat.grid(row=1, column=1, sticky="e")

        self.l_long = ttk.Label(self.poi_frame, text="Longitude (DD) : ")
        self.l_long.grid(row=2, column=0, sticky="w")
        self.poi_long = ttk.Entry(self.poi_frame)
        self.poi_long.grid(row=2, column=1, sticky="e")

        self.l_alt = ttk.Label(self.poi_frame, text="Altitude (m) : ")
        self.l_alt.grid(row=3, column=0, sticky="w")
        self.poi_alt = ttk.Entry(self.poi_frame)
        self.poi_alt.grid(row=3, column=1, sticky="e")

        ttk.Label(self.poi_frame, text="Color : ").grid(row=4, column=0, sticky="w")
        self.combo_color_poi = ttk.Combobox(self.poi_frame)
        self.combo_color_poi.grid(row=4, column=1, sticky="e")
        self.combo_color_poi['state'] = 'readonly'
        self.combo_color_poi.set(list_colors[0])
        self.combo_color_poi['values'] = list_colors

        ttk.Button(self.poi_frame, text="Select Countries", command=self.area_by_country).grid(row=5, column=0, pady=10)
        ttk.Button(self.poi_frame, text="Draw area", command=self.area_by_hand).grid(row=5, column=1, pady=10)
        ttk.Button(self.poi_frame, text="Choose mesh resolution", command=self.chooseres).grid(row=5, column=2, pady=10)
        ttk.Button(self.poi_frame, text="Import POI", command=self.importpoi).grid(row=6, column=1, pady=10)
        ttk.Button(self.poi_frame, text="Add POI", command=self.add_poi).grid(row=7, column=2, pady=10)
        ttk.Button(self.poi_frame, text="Modify POI", command=self.modify_poi).grid(row=7, column=1, pady=10)
        ttk.Button(self.poi_frame, text="Delete POI", command=self.delete_poi).grid(row=7, column=0, pady=10)

        self.l_gsn = ttk.Label(self.poi_frame, text="Name of the Ground Station : ")
        self.l_gsn.grid(row=8, column=0, sticky="w")
        self.gs_name = ttk.Entry(self.poi_frame)
        self.gs_name.grid(row=8, column=1, sticky="e")

        self.l_gslat = ttk.Label(self.poi_frame, text="Latitude (DD) : ")
        self.l_gslat.grid(row=9, column=0, sticky="w")
        self.gs_lat = ttk.Entry(self.poi_frame)
        self.gs_lat.grid(row=9, column=1, sticky="e")

        self.l_gslong = ttk.Label(self.poi_frame, text="Longitude (DD) : ")
        self.l_gslong.grid(row=10, column=0, sticky="w")
        self.gs_long = ttk.Entry(self.poi_frame)
        self.gs_long.grid(row=10, column=1, sticky="e")

        self.l_gsalt = ttk.Label(self.poi_frame, text="Altitude (m) : ")
        self.l_gsalt.grid(row=11, column=0, sticky="w")
        self.gs_alt = ttk.Entry(self.poi_frame)
        self.gs_alt.grid(row=11, column=1, sticky="e")

        self.l_gsant = ttk.Label(self.poi_frame, text="Antenna's diameter (m) : ")
        self.l_gsant.grid(row=12, column=0, sticky="w")
        self.gs_ant = ttk.Entry(self.poi_frame)
        self.gs_ant.grid(row=12, column=1, sticky="e")

        self.l_gsel = ttk.Label(self.poi_frame, text="Elevation (°) : ")
        self.l_gsel.grid(row=13, column=0, sticky="w")
        self.gs_ele = ttk.Entry(self.poi_frame)
        self.gs_ele.grid(row=13, column=1, sticky="e")

        ttk.Label(self.poi_frame, text="Band : ").grid(row=14, column=0, sticky="w")
        self.combo_bande = ttk.Combobox(self.poi_frame)
        self.combo_bande.grid(row=14, column=1, sticky="e")
        self.combo_bande['state'] = 'readonly'
        self.combo_bande.set(list_bande[0])
        self.combo_bande['values'] = list_bande

        self.l_gsdeb = ttk.Label(self.poi_frame, text="Debit (Mb/s) : ")
        self.l_gsdeb.grid(row=15, column=0, sticky="w")
        self.gs_deb = ttk.Entry(self.poi_frame)
        self.gs_deb.grid(row=15, column=1, sticky="e")

        ttk.Label(self.poi_frame, text="Color : ").grid(row=16, column=0, sticky="w")
        self.combo_color_gs = ttk.Combobox(self.poi_frame)
        self.combo_color_gs.grid(row=16, column=1, sticky="e")
        self.combo_color_gs['state'] = 'readonly'
        self.combo_color_gs.set(list_colors[0])
        self.combo_color_gs['values'] = list_colors

        ttk.Button(self.poi_frame, text="Import Ground Station", command=self.importgs).grid(row=17, column=1, pady=10)
        ttk.Button(self.poi_frame, text="Add Ground Station", command=self.add_gs).grid(row=18, column=2, pady=10)
        ttk.Button(self.poi_frame, text="Modify Ground Station", command=self.modify_gs).grid(row=18, column=1, pady=10)   
        ttk.Button(self.poi_frame, text="Delete Ground Station", command=self.delete_gs).grid(row=18, column=0, pady=10)       

    def tab5(self):

        self.__poi_temp = []
        self.__gs_temp = []
        self.mission_frame = ttk.LabelFrame(self.main_frame, text="Mission Creation :", padding=(10, 10),)
        self.mission_frame.place(relx=0.73, rely=0.57)

        self.l_mn = ttk.Label(self.mission_frame, text="Name of the Mission : ")
        self.l_mn.grid(row=0, column=0, sticky="w")
        self.mission_name = ttk.Entry(self.mission_frame)
        self.mission_name.grid(row=0, column=1, sticky="e")

        self.l_misstime = ttk.Label(self.mission_frame, text="Starting date of the mission (DD/MM/YYYY) : ")
        self.l_misstime.grid(row=1, column=0, sticky="w")
        self.mission_time = DateEntry(self.mission_frame, date_pattern="dd/mm/yyyy")
        self.mission_time.grid(row=1, column=1, sticky="e")
        
        self.l_misstime_end = ttk.Label(self.mission_frame, text="Ending date of the mission ((DD/MM/YYYY)) : ")
        self.l_misstime_end.grid(row=2, column=0, sticky="w")
        self.mission_time_end = DateEntry(self.mission_frame, date_pattern="dd/mm/yyyy")
        self.mission_time_end.grid(row=2, column=1, sticky="e")

        self.l_timestep = ttk.Label(self.mission_frame, text="Time step of the mission (s) : ")
        self.l_timestep.grid(row=3, column=0, sticky="w")
        self.timestep = ttk.Entry(self.mission_frame)
        self.timestep.grid(row=3, column=1, sticky="e")

        ttk.Label(self.mission_frame, text="Type : ").grid(row=4, column=0, sticky="w")
        self.combo_mission_type = ttk.Combobox(self.mission_frame)
        self.combo_mission_type.grid(row=4, column=1, sticky="e")
        self.combo_mission_type['state'] = 'readonly'
        self.combo_mission_type.set(sat_type[0])
        self.combo_mission_type['values'] = sat_type

        self.l_sza = ttk.Label(self.mission_frame, text="Minimun Sun Zenith Angle (°) : ")
        self.l_sza.grid(row=5, column=0, sticky="w")
        self.minsza = ttk.Entry(self.mission_frame)
        self.minsza.grid(row=5, column=1, sticky="e")

        self.l_combo_poi = ttk.Label(self.mission_frame, text="Poi : ")
        self.l_combo_poi.grid(row=6, column=0, sticky="w")
        self.combo_poi = ttk.Combobox(self.mission_frame, postcommand= self.comb_poi_upd)
        self.combo_poi.grid(row=6, column=1, sticky="e")
        self.combo_poi['state'] = 'readonly'
        self.combo_poi.set('Choose a POI...')

        self.l_combo_gs = ttk.Label(self.mission_frame, text="GS : ")
        self.l_combo_gs.grid(row=7, column=0, sticky="w")
        self.combo_gs = ttk.Combobox(self.mission_frame, postcommand= self.comb_gs_upd)
        self.combo_gs.grid(row=7, column=1, sticky="e")
        self.combo_gs['state'] = 'readonly'
        self.combo_gs.set('Choose a GS...')

        self.l_combo_const = ttk.Label(self.mission_frame, text="Constellation : ")
        self.l_combo_const.grid(row=8, column=0, sticky="w")
        self.combo_const = ttk.Combobox(self.mission_frame, postcommand= self.comb_const_upd)
        self.combo_const.grid(row=8, column=1, sticky="e")
        self.combo_const['state'] = 'readonly'
        self.combo_const.set('Choose a Constellation...')

        ttk.Button(self.mission_frame, text="Add Mission", command=self.add_mission).grid(row=9, column=0, columnspan=2, pady=10)
        ttk.Button(self.mission_frame, text="Associate", command=self.ass_gs_mission).grid(row=7, column=2, columnspan=2, pady=10)
        ttk.Button(self.mission_frame, text="Associate", command=self.ass_poi_mission).grid(row=6, column=2, columnspan=2, pady=10)

    def tab6(self):
        # Frame for simulation control
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Simulation :", padding=(10, 10))
        
        self.control_frame.place(relx =0.38, rely= 0.88)

        ttk.Label(self.control_frame, text="Mission : ").grid(row=0, column=0, sticky="w")
        self.combo_mission = ttk.Combobox(self.control_frame, postcommand= self.comb_miss_upd)
        self.combo_mission.grid(row=0, column=1, sticky="e")
        self.combo_mission['state'] = 'readonly'
        self.combo_mission.set('Choose a Mission...')

        ttk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation).grid(row=1, column=0, pady=5)
        ttk.Button(self.control_frame, text="Save Simulation", command=self.save_simulation).grid(row=1, column=1, pady=5)
        ttk.Button(self.control_frame, text="Load Simulation", command=self.load_simulation).grid(row=1, column=2, pady=5)
        ttk.Button(self.control_frame, text="Reset", command=self.reset).grid(row=1, column=3, pady=5)
       
    def add_satellite(self):
        i=0
        if len(self.sat_name.get())== 0:
            self.l_sn.config(foreground = "red")
            i=+1
        else:
            self.l_sn.config(foreground = "green")
        if self.validate_entry(self.sat_swath.get())== False:
            self.l_sw.config(foreground = "red")
            i=+1
        elif float(self.sat_swath.get()) < 0:
            self.l_sw.config(foreground = "orange")
            showinfo("Message", "The satellite's swath must be positive !")
            i=+1
        else:
            self.l_sw.config(foreground = "green")

        if self.validate_entry(self.sat_dep.get())== False:
            self.l_dep.config(foreground = "red")
            i=+1
        elif float(self.sat_dep.get()) < 0 or float(self.sat_dep.get()) > 45:
            self.l_dep.config(foreground = "orange")
            showinfo("Message", "The satellite's depointing must be positbetween 0° and 45° !")
            i=+1
        else:
            self.l_dep.config(foreground = "green")
        
        if self.validate_entry(self.altitude.get()) == False:
            self.l_a.config(foreground = "red")
            i=+1
        elif float(self.altitude.get()) <= 200:
            showinfo("Message", "The altitude must be higher than 200km !")
            self.l_a.config(foreground = "orange")
            i=+1
        else:
            self.l_a.config(foreground = "green")
        if self.validate_entry(self.eccentricity.get())== False:
            self.l_e.config(foreground = "red")
            i=+1
        elif float(self.eccentricity.get()) < 0 or float (self.eccentricity.get()) >= 1:
            showinfo("Message", "The eccentricity must be between 0 and 1 !")
            self.l_e.config(foreground = "orange")
            i=+1
        else:
            self.l_e.config(foreground = "green")
        if self.validate_entry(self.inclination.get())== False:
            self.l_i.config(foreground = "red")
            i=+1
        elif float(self.inclination.get()) < 0 or float(self.inclination.get()) > 180:
            showinfo("Message", "The inclination must be between 0° and 180° !")
            self.l_i.config(foreground = "orange")
            i=+1
        else:
            self.l_i.config(foreground = "green")
        if self.validate_entry(self.raan.get())== False:
            self.l_raan.config(foreground = "red")
            i=+1
        elif float(self.raan.get()) < 0 or float(self.raan.get()) > 360:
            self.l_raan.config(foreground = "orange")
            showinfo("Message", "The RAAN must be between 0° and 360° !")
            i=+1
        else:
            self.l_raan.config(foreground = "green")
        if self.validate_entry(self.arg_perigee.get())== False:
            self.l_ap.config(foreground = "red")
            i=+1
        elif float(self.arg_perigee.get()) < 0 or float(self.arg_perigee.get()) > 360:
            self.l_ap.config(foreground = "orange")
            showinfo("Message", "The argument of perigee must be between 0° and 360° !")
            i=+1
        else:
            self.l_ap.config(foreground = "green")
        if self.validate_entry(self.true_anomaly.get())== False:
            self.l_ta.config(foreground = "red")
            i=+1
        elif float(self.true_anomaly.get()) < 0 or float(self.true_anomaly.get()) > 360:
            self.l_ta.config(foreground = "orange")
            showinfo("Message", "The true anomaly must be between 0° and 360° !")
            i=+1
        else:
            self.l_ta.config(foreground = "green")

        if i==0:
            orb = init_orb(float(self.altitude.get()),
                            float(self.eccentricity.get()),
                            float(self.inclination.get()),
                            float(self.raan.get()),
                            float(self.arg_perigee.get()),
                            float(self.true_anomaly.get()))
            sat = init_sat(str(self.sat_name.get()), 
                           float(self.sat_swath.get()),
                           float(self.sat_dep.get()),
                           str(self.combo_color.get()),
                           str(self.combo_type.get()), orb)
            liste_satellite.append(sat)
            self.flag_mod_sat = False
            showinfo("Message", "Satellite added successfully !")
            [widget.delete(0, tk.END) for widget in self.sat_frame.winfo_children() if isinstance(widget, tk.Entry)]
        else:
            showinfo("Error", "One or more parameters are incorrect !")

    def modify_satellite(self):
        if self.flag_mod_sat == False:
            window = ModifySatelliteWindow(self.showsatelliteinfo)
        else:
            self.flag_mod_sat = False
            for i in range(len(liste_satellite)):
                if liste_satellite[i].get_name() == str(self.sat_name.get()):
                    liste_satellite[i].set_name(str(self.sat_name.get()))
                    liste_satellite[i].set_swath(float(self.sat_swath.get()))
                    liste_satellite[i].set_depointing(float(self.sat_dep.get()))
                    liste_satellite[i].set_color(str(self.combo_color.get()))
                    liste_satellite[i].set_type(str(self.combo_type.get()))

                    orb = liste_satellite[i].get_orbit()
                    orb.set_semi_major_axis(float(self.altitude.get()))
                    orb.set_eccentricity(float(self.eccentricity.get()))
                    orb.set_inclination(float(self.inclination.get()))
                    orb.set_raan(float(self.raan.get()))
                    orb.set_arg_peri(float(self.arg_perigee.get()))
                    orb.set_true_ano(float(self.true_anomaly.get()))
                    liste_satellite[i].set_orbit(orb)
            showinfo("Message", "Satellite modified with success")

    def delete_satellite(self):
        showinfo("Message", "NOT IMPLEMENTED YET")

    def showsatelliteinfo(self, satname):
        for i in range(len(liste_satellite)):
            if liste_satellite[i].get_name() == satname:
                self.sat_name.insert(0, liste_satellite[i].get_name())
                self.sat_swath.insert(0, liste_satellite[i].get_swath())
                self.sat_dep.insert(0, liste_satellite[i].get_depoiting())
                self.combo_type.set(liste_satellite[i].get_type())
                self.combo_color.set(liste_satellite[i].get_color())

                orb = liste_satellite[i].get_orbit()
                a, e, ic, Ω, ω, ν = orb.get_all()
                a = (a-6378e3)/1000
                self.altitude.insert(0, a)
                self.eccentricity.insert(0, e)
                self.inclination.insert(0, ic)
                self.raan.insert(0, Ω)
                self.arg_perigee.insert(0, ω)
                self.true_anomaly.insert(0, ν)
        showinfo('Message', 'Done, to confirm the change, re-click on "Modify Satellite"')
        self.flag_mod_sat = True

    def openTLEwindow(self):
        window = FetchTLEWindow(self.fetchTLEdata)

    def fetchTLEdata(self, noradID):
        try:
            tle=fetch_tle_from_celestrak(noradID)
            showinfo('Message', f"{tle[0]} has been found !")
            self.sat_name.delete(0, tk.END)
            self.sat_name.insert(0, tle[0])
            orbital_data = tle[2].split()
            self.inclination.delete(0, tk.END)
            self.inclination.insert(0, orbital_data[2])
            self.raan.delete(0, tk.END)
            self.raan.insert(0, orbital_data[3])
            self.eccentricity.delete(0, tk.END)
            self.eccentricity.insert(0, "0."+orbital_data[4])
            self.arg_perigee.delete(0, tk.END)
            self.arg_perigee.insert(0, orbital_data[5])
        
            a=((mu**(1/3))/(((2*float(orbital_data[7])*np.pi)/86400)**(2/3)) - earth_radius)/1000
            self.altitude.delete(0, tk.END)
            self.altitude.insert(0, a)
            self.true_anomaly.delete(0, tk.END)
            ta = true_anomaly(float(orbital_data[6]), float("0."+orbital_data[4]) )
            self.true_anomaly.insert(0, ta)
        except IndexError:
            showinfo("Error", "The NORAD ID does not correspond to any existing satellite")
        
    def add_constellation(self):
        i=0
        if len(self.const_name.get())== 0:
            self.l_consn.config(foreground = "red")
            i=+1
        else:
            self.l_consn.config(foreground = "green")
        if self.validate_entry(self.walkerT.get())== False:
            self.l_walkerT.config(foreground = "red")
            i=+1
        elif float(self.walkerT.get()) <= 0:
            self.l_walkerT.config(foreground = "orange")
            showinfo("Message", "The number of satellites must be positive")
            i=+1
        else:
            self.l_walkerT.config(foreground = "green")
        if self.validate_entry(self.walkerP.get()) == False:
            self.l_walkerP.config(foreground = "red")
            i=+1
        elif float(self.walkerP.get()) <= 0:
            self.l_walkerP.config(foreground = "orange")
            showinfo("Message", "The number of orbital planes must be positive")
            i=+1
        else:
            self.l_walkerP.config(foreground = "green")
        if self.validate_entry(self.walkerF.get())== False:
            self.l_walkerF.config(foreground = "red")
            i=+1
        elif float(self.walkerF.get()) < 0:
            self.l_walkerF.config(foreground = "orange")
            showinfo("Message", "The phasing factor must be positive")
            i=+1
        else:
            self.l_walkerF.config(foreground = "green")
        
        if (str(self.combo_sat.get()) == 'Choose a model...') or (str(self.combo_sat.get()) == 'Aucun'):
            #print("You need to choose a model !!!")
            self.l_combo_sat.config(foreground = "red")
            i=+1
        else:
            self.l_combo_sat.config(foreground = "green")
        
        if i==0:
            for i in range(len(liste_satellite)):
                if liste_satellite[i].get_name() == str(self.combo_sat.get()):
                    cons = init_constellation(str(self.const_name.get()),
                                float(self.walkerP.get()),
                                float(self.walkerT.get()),
                                float(self.walkerF.get()),
                                str(self.combo_color_const.get()),
                                liste_satellite[i])
                    liste_constellation.append(cons)
                    showinfo("Message", "Constellation added successfully !")
                    [widget.delete(0, tk.END) for widget in self.const_frame.winfo_children() if isinstance(widget, tk.Entry)]
        else:
            showinfo("Error", "One or more parameters are incorrect !")

    def modify_constellation(self):
        if self.flag_mod_const == False:
            window = ModifyConstellationWindow(self.showconstellationinfo)
        else:
            self.flag_mod_const = False
            for i in range(len(liste_constellation)):
                if liste_constellation[i]== str(self.const_name.get()):
                    liste_constellation[i].set_name(str(self.const_name.get()))
                    liste_constellation[i].set_walkerP(float(self.walkerP.get()))
                    liste_constellation[i].set_walkerT(float(self.walkerT.get()))
                    liste_constellation[i].set_walkerF(float(self.walkerF.get()))
                    liste_constellation[i].set_color(str(self.combo_color_const.get()))
                    for j in range(len(liste_satellite)):
                        if liste_satellite[j].get_name() == str(self.combo_sat.get()):
                            liste_constellation[i].set_model(liste_satellite[j])
            showinfo("Message", "Constellation modified with success")

    def delete_constellation(self):
        showinfo("Message", "NOT IMPLEMENTED YET")

    def showconstellationinfo(self, constname):
        for i in range(len(liste_constellation)):
            if liste_constellation[i].get_name() == constname:
                self.const_name.insert(0, liste_constellation[i].get_name())
                self.walkerP.insert(0, liste_constellation[i].get_walkerP())
                self.walkerT.insert(0, liste_constellation[i].get_walkerT())
                self.walkerF.insert(0, liste_constellation[i].get_walkerF())
                self.combo_color_const.set(liste_constellation[i].get_color())
                sat = liste_constellation[i].get_model()
                self.combo_sat.set(sat.get_name())
        showinfo('Message', 'Done, to confirm the change, re-click on "Modify Constellation"')
        self.flag_mod_const = True

    def add_poi(self):
        i=0
        if len(self.poi_name.get())== 0:
            self.l_poin.config(foreground = "red")
            i=+1
        else:
            self.l_poin.config(foreground = "green")
        if self.flag_area==False:
            if (self.validate_entry(self.poi_lat.get())== False):
                self.l_lat.config(foreground = "red")
                i=+1
            elif (float(self.poi_lat.get()) < -90 or float(self.poi_lat.get()) > 90):
                self.l_lat.config(foreground = "orange")
                showinfo("Message", "The lalitude must be between -90° and 90°")
                i=+1
            else:
                self.l_lat.config(foreground = "green")
            if (self.validate_entry(self.poi_long.get())== False):
                self.l_long.config(foreground = "red")
                i=+1
            elif (float(self.poi_long.get()) < -180 or float(self.poi_long.get()) > 180):
                self.l_long.config(foreground = "orange")
                showinfo("Message", "The longitude must be between -180° and 180°")
                i=+1
            else:
                self.l_long.config(foreground = "green")
        
        if self.validate_entry(self.poi_alt.get()) == False:
            self.l_alt.config(foreground = "red")
            i=+1
        elif float(self.poi_alt.get()) < 0:
            self.l_alt.config(foreground = "orange")
            showinfo("Message", "The altitude must be positive")
            i=+1
        else:
            self.l_alt.config(foreground = "green")
        if i==0:
            if self.flag_area==False:
                coord = [float(self.poi_long.get()), float(self.poi_lat.get())]
            elif self.flag_country == True:
                coord = self.selected_country_coords
                grid = self.grid_coords
                poly_grid = self.grid_poly
            else:
                coord = self.marker_list
                grid = self.grid_coords
                poly_grid = self.grid_poly
            
            poi = init_poi(str(self.poi_name.get()),
                           coord,
                           float(self.poi_alt.get()),
                           str(self.combo_color_poi.get()),
                           self.flag_area)
            if self.flag_area == True or self.flag_country == True:
                poi.set_grid(grid)
                poi.set_poly(poly_grid)
                if len(poly_grid)!=1:
                    poi.set_multi()
            liste_poi.append(poi)
            self.poi_lat.config(state="enable")
            self.poi_long.config(state="enable")
            self.poi_name.config(state="enable")
            for i in range(len(self.marker_poi)):
                self.marker_poi[i].delete()
            self.marker_list = []
            self.grid_coords = []
            self.grid_poly = []
            self.selected_country_coords = []
            self.country_marker = []
            if self.flag_area==False:
                poi_marker = self.__map_widget.set_marker(poi.get_coordinate(0)[0], poi.get_coordinate(0)[1], text=poi.get_name(), marker_color_circle= "yellow", marker_color_outside=poi.get_color())
            else:
                self.final_poly_list.append(self.poly_list[0])
                self.poly_list = []
            self.flag_area=False
            self.flag_country = False
            showinfo("Message", "POI added succesfully")
            [widget.delete(0, tk.END) for widget in self.poi_frame.winfo_children() if isinstance(widget, tk.Entry)]
        else:
            showinfo("Error", "One or more parameters are incorrect !")

    def modify_poi(self):
        if self.flag_mod_poi == False:
            window = ModifyPOIWindow(self.showpoiinfo)
        else:
            self.flag_mod_poi = False
            for i in range(len(liste_poi)):
                if liste_poi[i].get_name() == str(self.poi_name.get()):
                    liste_poi[i].set_name(str(self.poi_name.get()))
                    liste_poi[i].reset_coordinate()
                    liste_poi[i].set_coordinate(float(self.poi_lat.get()), float(self.poi_long.get()))
                    liste_poi[i].set_altitude(float(self.poi_alt.get()))
                    liste_poi[i].set_color(str(self.combo_color_poi.get()))
            showinfo("Message", "Point of interest modified with success")

    def delete_poi(self):
        showinfo("Message", "NOT IMPLEMENTED YET")

    def showpoiinfo(self, poiname):
        for i in range(len(liste_poi)):
            if liste_poi[i].get_name() == poiname:
                self.poi_name.insert(0, liste_poi[i].get_name())
                self.poi_long.insert(0, liste_poi[i].get_coordinate(0)[1])
                self.poi_lat.insert(0, liste_poi[i].get_coordinate(0)[0])
                self.poi_alt.insert(0, liste_poi[i].get_altitude())
                self.combo_color_poi.set(liste_poi[i].get_color())
        showinfo('Message', 'Done, to confirm the change, re-click on "Modify POI"')
        self.flag_mod_poi = True

    def importpoi(self):
        filename = askopenfilename(title="Choose a file containing POIs information", filetypes=[("CSV file", "*.csv")])
        print(filename)
        er = import_poi_csv(filename)
        if er==0:
            for i in range(len(liste_poi)):
                if liste_poi[i].IsArea()== False:
                    poi_marker = self.__map_widget.set_marker(liste_poi[i].get_coordinate(0)[0], liste_poi[i].get_coordinate(0)[1], text=liste_poi[i].get_name(), marker_color_outside=liste_poi[i].get_color())
                else:
                    if liste_poi[i].get_multi():
                        liste_poi[i].set_multipoly(liste_poi[i].get_area())
                        coords = liste_poi[i].get_area()
                        for j in range(len(coords)):
                            poly = self.__map_widget.set_polygon(coords[j], outline_color=liste_poi[i].get_color(), fill_color=liste_poi[i].get_color(), name=liste_poi[i].get_name())
                    else:
                        poly = self.__map_widget.set_polygon(liste_poi[i].get_area(), outline_color=liste_poi[i].get_color(), fill_color=liste_poi[i].get_color(), name=liste_poi[i].get_name())
                    self.grid_show_test(liste_poi[i].get_area())
                    grid = self.grid_coords
                    poly_grid = self.grid_poly
                    liste_poi[i].set_grid(grid)
                    liste_poi[i].set_poly(poly_grid)
                    self.grid_coords = []
                    self.grid_poly = []
            showinfo("Message", "POIs loaded succesfully")
        else:
            showinfo("Error", "Something went wrong !")
        
    def importgs(self):
        filename = askopenfilename(title="Choose a file containing GSs information", filetypes=[("CSV file", "*.csv")])
        print(filename)
        er = import_gs_csv(filename)
        if er==0:
            for i in range(len(liste_gs)):
                gs_marker = self.__map_widget.set_marker(liste_gs[i].get_coordinate()[0], liste_gs[i].get_coordinate()[1], text=liste_gs[i].get_name(), marker_color_outside=liste_gs[i].get_color())
            showinfo("Message", "GSs loaded succesfully")
        else:
            showinfo("Error", "Something went wrong !")

    def add_gs(self):
        i=0
        if len(self.gs_name.get())== 0:
            self.l_gsn.config(foreground = "red")
            i=+1
        else:
            self.l_gsn.config(foreground = "green")
        if self.validate_entry(self.gs_lat.get())== False:
            self.l_gslat.config(foreground = "red")
            i=+1
        elif float(self.gs_lat.get()) < -90 or float(self.gs_lat.get()) > 90:
            self.l_gslat.config(foreground = "orange")
            showinfo("Message", "Latitude must be between -90° and 90° !")
            i=+1
        else:
            self.l_gslat.config(foreground = "green")
        if self.validate_entry(self.gs_long.get())== False:
            self.l_gslong.config(foreground = "red")
            i=+1
        elif float(self.gs_long.get()) < -180 or float(self.gs_long.get()) > 180:
            self.l_gslong.config(foreground = "orange")
            showinfo("Message", "Longitude must be between -180° and 180° !")
            i=+1
        else:
            self.l_gslong.config(foreground = "green")

        if self.validate_entry(self.gs_alt.get()) == False:
            self.l_gsalt.config(foreground = "red")
            i=+1
        elif float(self.gs_alt.get()) < 0:
            self.l_gsalt.config(foreground = "orange")
            showinfo("Message", "Altitude must be positive !")
            i=+1
        else:
            self.l_gsalt.config(foreground = "green")
        if self.validate_entry(self.gs_ele.get())== False:
            self.l_gsel.config(foreground = "red")
            i=+1
        elif float(self.gs_ele.get()) < 0:
            self.l_gsel.config(foreground = "orange")
            showinfo("Message", "Elevation must be positive !")
            i=+1
        else:
            self.l_gsel.config(foreground = "green")
        if self.validate_entry(self.gs_ant.get())== False:
            self.l_gsant.config(foreground = "red")
            i=+1
        elif float(self.gs_ant.get()) < 0:
            self.l_gsant.config(foreground = "orange")
            showinfo("Message", "The antenna's diameter must be positive !")
            i=+1
        else:
            self.l_gsant.config(foreground = "green")
        if self.validate_entry(self.gs_deb.get())== False:
            self.l_gsdeb.config(foreground = "red")
            i=+1
        elif float(self.gs_deb.get()) < 0:
            self.l_gsdeb.config(foreground = "orange")
            showinfo("Message", "Debit must be positive !")
            i=+1
        else:
            self.l_gsdeb.config(foreground = "green")

        if i==0:
            gs = init_gs( str(self.gs_name.get()),
                           float(self.gs_long.get()),
                           float(self.gs_lat.get()),
                           float(self.gs_alt.get()),
                           float(self.gs_ele.get()),
                           str(self.combo_bande.get()),
                           float(self.gs_deb.get()),
                           float(self.gs_ant.get()),
                           str(self.combo_color_gs.get()))
            liste_gs.append(gs)
            print("Ground Station added successfully !")
            gs_marker = self.__map_widget.set_marker(gs.get_coordinate()[0], gs.get_coordinate()[1], text=gs.get_name(), marker_color_circle= "blue", marker_color_outside=gs.get_color())
            showinfo("Message", "GS added successfuly !")
            [widget.delete(0, tk.END) for widget in self.poi_frame.winfo_children() if isinstance(widget, tk.Entry)]
        else:
            showinfo("Error", "One or more parameters are incorrect !")

    def modify_gs(self):
        if self.flag_mod_gs == False:
            window = ModifyGSWindow(self.showgsinfo)
        else:
            self.flag_mod_gs = False
            for i in range(len(liste_gs)):
                if liste_gs[i].get_name() == str(self.gs_name.get()):
                    liste_gs[i].set_name(str(self.gs_name.get()))
                    liste_gs[i].set_latitude(float(self.gs_lat.get()))
                    liste_gs[i].set_longitude(float(self.gs_long.get()))
                    liste_gs[i].set_altitude(float(self.gs_alt.get()))
                    liste_gs[i].set_elevation(float(self.gs_ele.get()))
                    liste_gs[i].set_bandwidth(float(self.gs_bw.get()))
                    liste_gs[i].set_debit(float(self.gs_deb.get()))
                    liste_gs[i].set_antenna(float(self.gs_ant.get()))
                    liste_gs[i].set_color(str(self.combo_color_gs.get()))
            showinfo("Message", "Ground Station modified with success")

    def delete_gs(self):
        showinfo("Message", "NOT IMPLEMENTED YET")

    def showgsinfo(self, gsname):
        for i in range(len(liste_gs)):
            if liste_gs[i].get_name() == gsname:
                self.gs_name.insert(0, liste_gs[i].get_name())
                lat, long = liste_gs[i].get_coordinate()
                self.gs_lat.insert(0, lat)
                self.gs_long.insert(0, long)
                self.gs_alt.insert(0, liste_gs[i].get_altitude())
                self.gs_ele.insert(0, liste_gs[i].get_elevation())
                self.gs_bw.insert(0, liste_gs[i].get_bandwidth())
                self.gs_deb.insert(0, liste_gs[i].get_debit())
                self.gs_ant.insert(0, liste_gs[i].get_antenna())
                self.combo_color_gs.set(liste_gs[i].get_color())
        showinfo('Message', 'Done, to confirm the change, re-click on "Modify Ground Station"')
        self.flag_mod_const = True

    def add_mission(self):
        i=0
        if len(self.mission_name.get())== 0:
            self.l_mn.config(foreground = "red")
            i=+1
        else:
            self.l_mn.config(foreground = "green")
        if self.validate_entry(self.timestep.get()) == False:
            self.l_timestep.config(foreground = "red")
            i=+1
        elif float(self.timestep.get()) <= 0:
            self.l_timestep.config(foreground = "orange")
            showinfo("Message", "Timestep must be higher than 0 !")
            i=+1
        else:
            self.l_timestep.config(foreground = "green")
            
        if self.validate_entry(self.minsza.get()) == False:
            self.l_sza.config(foreground = "red")
            i=+1
        elif float(self.minsza.get()) <= 0:
            self.l_sza.config(foreground = "orange")
            showinfo("Message", "SZA must be higher than 0 !")
            i=+1
        else:
            self.l_sza.config(foreground = "green")
        if (str(self.combo_const.get()) == 'Choose a Constellation...') or (str(self.combo_const.get()) == 'Aucun'):
            self.l_combo_const.config(foreground = "red")
            i=+1
        else:
            self.l_combo_const.config(foreground = "green")

        if len(self.__gs_temp) == 0:
            i=+1
            self.l_combo_gs.config(foreground = "red")
        else:
            self.l_combo_gs.config(foreground = "green")
        if len(self.__poi_temp) == 0:
            i=+1
            self.l_combo_poi.config(foreground = "red")
        else:
            self.l_combo_poi.config(foreground = "green")
        if i==0:
            mission = init_mission(str(self.mission_name.get()),
                                   float(self.timestep.get()),
                                   self.mission_time.get_date(),
                                   self.mission_time_end.get_date(),
                                   str(self.combo_mission_type.get()),
                                   float(self.minsza.get()),
                                   self.__poi_temp,
                                   self.__gs_temp,
                                   str(self.combo_const.get()))
            liste_mission.append(mission)
            showinfo("Message", "Mission added successfully !")
            [widget.delete(0, tk.END) for widget in self.mission_frame.winfo_children() if isinstance(widget, tk.Entry)]
        else:
            showinfo("Error", "One or more parameters are incorrect !")

    def chooseres(self):
        window = ChooseResolutionWindow(self.spatialres)

    def spatialres(self, res):
        folder = Path(f"dataset/{res}/")
        path_to_shapefile = folder / f"ne_{res}m_admin_0_map_units.shp"
        world = gpd.read_file(path_to_shapefile)

    def area_by_country(self):
        if len(self.poly_list)==0:
            country_name, state_name = get_country_name(self.country_coords)
            if country_name is None:
                showinfo("Error", "You must select a valid country")
            else:
                coords, name = get_poly_coordinate(country_name, state_name)
                self.poi_name.delete(0, tk.END)
                self.poi_name.insert(0, name)
                self.poi_name.config(state="disable")
                self.poi_lat.config(state="disable")
                self.poi_long.config(state="disable")
                print(name)
                poly_correct_coords = [] 
                for i in range(len(coords)):
                    correct_coords =[]
                    for k in range(len(coords[i])):
                        temp = coords[i][k]
                        lat = temp[0]
                        long = temp[1]
                        correct_coords.append((long, lat))
                    poly_correct_coords.append(correct_coords)
                
                for i in range(len(poly_correct_coords)):   
                    poly = self.__map_widget.set_polygon(poly_correct_coords[i], outline_color="red", fill_color="green", name=name)
                    self.poly_list.append(poly)
                    self.selected_country_coords.append(poly_correct_coords[i])
                
                self.flag_area = True
                self.flag_country = True
                self.flag_marker = False
                self.country_marker[0].delete()
                self.country_marker.clear()
                self.country_coords.clear()
                self.grid_show_test(self.selected_country_coords)
        else:
            showinfo("Error", "Area already created")  
        
    def area_by_hand(self):
        if len(self.poly_list)==0:
            self.poi_lat.config(state="disable")
            self.poi_long.config(state="disable")
            poly_name = f"{len(self.poly_list)+1}"
            
            poly = self.__map_widget.set_polygon(self.marker_list, outline_color="blue", fill_color="green", name=poly_name)
            self.poly_list.append(poly)
            self.grid_show_test(self.marker_list)   
            self.flag_area = True
            
        else:
            showinfo("Error", "Area already created")  
        return

    def grid_show_test(self, coords):
        list_coords = []
        list_poly = []
        #Réorganise les coordonnées pour creer des polygons
        if len(coords) == 1:
            for i in range(len(coords[0])):
                temp = coords[0][i]
                list_coords.append([temp[1], temp[0]])
        else:
            for i in range(len(coords)):
                if len(coords[i]) == 2:
                    list_coords.append([coords[i][1], coords[i][0]])
                else:
                    for j in range(len(coords[i])):
                        temp = coords[i][j]
                        list_coords.append([temp[1], temp[0]])
                    list_poly.append(list_coords)
                    list_coords = []
        #Créé la grille dans le polygon et l'affiche
        if len(list_poly) == 0:
            poly = Polygon(list_coords)
            grid = partition(poly)    
            for grid_poly in grid:
                self.grid_coords.append(grid_poly)
            self.grid_poly.append(poly)
            #fig, ax = plt.subplots(figsize=(15, 15))
            #gpd.GeoSeries(grid).boundary.plot(ax=ax)
            #gpd.GeoSeries([poly]).boundary.plot(ax=ax,color="red")
            #plt.show()
        else:
            poly = []
            grid = []
            for i in range(len(list_poly)): 
                poly.append(Polygon(list_poly[i]))
            for i in range(len(poly)):
                grid.append(partition(poly[i]))
            #fig, ax = plt.subplots(figsize=(15, 15))
            for i in range(len(grid)):
                if grid[i] ==None:
                    pass
                else:
                    temp_coords = []
                    #gpd.GeoSeries(grid[i]).boundary.plot(ax=ax)
                    self.grid_poly.append(poly[i]) 
                    #gpd.GeoSeries([poly[i]]).boundary.plot(ax=ax,color="red")
                    for grid_poly in grid[i]:
                        temp_coords.append(grid_poly)
                    self.grid_coords.append(temp_coords)
            #plt.show()

    def copy_coords_poi(self, coord):
        self.poi_lat.insert(0, coord[0])
        self.poi_long.insert(0, coord[1])
    
    def copy_coords_gs(self, coord):
        self.gs_lat.insert(0, coord[0])
        self.gs_long.insert(0, coord[1])

    def add_marker_hand(self, coords):
        marker_name = f"{len(self.marker_list)+1}"
        marker = self.__map_widget.set_marker(coords[0], coords[1], text=marker_name)
        self.marker_poi.append(marker)
        self.marker_list.append(marker.position)

    def add_marker_country(self, coords):
        if len(self.country_marker)!=0:
            self.country_marker[0].delete()
            self.country_marker.clear()
            self.country_coords.clear()
        marker= self.__map_widget.set_marker(coords[0], coords[1], text="Country")
        self.country_marker.append(marker)
        lat, long = marker.position
        self.country_coords.append((lat, long))
        
    def validate_entry(self, entry):
        if len(entry) == 0:
            return False
        elif entry:
            try:
                float(entry)
                return True
            except ValueError:
                return False

    def comb_const_upd(self):
        if len(liste_constellation)==0:
            self.combo_const['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_constellation)):
                temp.append(liste_constellation[i].get_name())
            self.combo_const['values'] = temp
    
    def comb_sat_upd(self):
        if len(liste_satellite)==0:
            self.combo_sat['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_satellite)):
                temp.append(liste_satellite[i].get_name())
            self.combo_sat['values'] = temp

    def comb_poi_upd(self):
        if len(liste_poi)==0:
            self.combo_poi['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_poi)):
                temp.append(liste_poi[i].get_name())
            self.combo_poi['values'] = temp
    
    def comb_gs_upd(self):
        if len(liste_gs)==0:
            self.combo_gs['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_gs)):
                temp.append(liste_gs[i].get_name())
            self.combo_gs['values'] = temp

    def comb_miss_upd(self):
        if len(liste_mission)==0:
            self.combo_mission['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_mission)):
                temp.append(liste_mission[i].get_name())
            self.combo_mission['values'] = temp    

    def comb_miss_simu(self):
        if len(self.calcul_marker)==0:
            self.comb_aff_sat['values'] = 'Aucun'
        else:
            temp=[]
            temp.append("All")
            for i in range(len(liste_mission)):
                if liste_mission[i].get_name()==str(self.combo_mission.get()):
                    cons = liste_mission[i].get_constellation()
                    for j in range(int(cons.get_walkerT())):
                        sat = cons.get_sat(j)
                        temp.append(sat.get_name())
            self.comb_aff_sat['values'] = temp
                    
    def ass_poi_mission(self):
        if (str(self.combo_poi.get()) == 'Choose a POI...') or (str(self.combo_poi.get()) == 'Aucun'):
            print("You need to choose a POI to continue")
            self.l_combo_poi.config(foreground= "red")
        else:
            self.l_combo_poi.config(foreground= "green")
            for i in range(len(liste_poi)):
                if liste_poi[i].get_name() == str(self.combo_poi.get()):
                    self.__poi_temp.append(liste_poi[i])
                    print("POI associate with mission")

    def ass_gs_mission(self):
        if (str(self.combo_gs.get()) == 'Choose a GS...') or (str(self.combo_gs.get()) == 'Aucun'):
            print("You need to choose a GS to continue")
            self.l_combo_gs.config(foreground= "red")
        else:
            self.l_combo_gs.config(foreground= "green")
            for i in range(len(liste_gs)):
                if liste_gs[i].get_name() == str(self.combo_gs.get()):
                    self.__gs_temp.append(liste_gs[i])
                    print("GS associate with mission")

    def run_simulation(self):
        if (len(liste_mission) == 0) or (str(self.combo_mission.get())=='Aucun') or(str(self.combo_mission.get())=='Choose a Mission'):
            showinfo("Error", "You need to select a mission to continue")
        else:
            for i in range(len(liste_mission)):
                if liste_mission[i].get_name()==str(self.combo_mission.get()):
                     self.calcul_marker = calcul_traj(liste_mission[i], self.__map_widget)
            #showinfo("Message", "Simulation simulated correctly")
            self.comb_aff_sat.config(state='enable')
                              
    def reset(self):
        self.__map_widget.delete_all_marker()
        self.__map_widget.delete_all_path()
        self.__map_widget.delete_all_polygon()
        self.set_map_default()
        reset_liste()
        self.flag_area = False
        self.flag_country = False
        self.flag_mod_sat = False
        self.flag_mod_const = False
        self.flag_mod_gs = False
        self.flag_mod_poi = False
        self.marker_list=[]
        self.marker_poi = []
        self.poly_list = []
        self.final_poly_list = []
        self.country_coords =[]
        self.country_marker =[]
        self.selected_country_coords = []
        self.comb_aff_sat.config(state='disable')
        [widget.delete(0, tk.END) for widget in self.sat_frame.winfo_children() if isinstance(widget, tk.Entry)]
        [widget.delete(0, tk.END) for widget in self.const_frame.winfo_children() if isinstance(widget, tk.Entry)]
        [widget.delete(0, tk.END) for widget in self.poi_frame.winfo_children() if isinstance(widget, tk.Entry)]
        [widget.delete(0, tk.END) for widget in self.mission_frame.winfo_children() if isinstance(widget, tk.Entry)]
        [widget.delete(0, tk.END) for widget in self.control_frame.winfo_children() if isinstance(widget, tk.Entry)]
        showinfo("Message", "Simulation reset")

    def save_simulation(self):
        if len(liste_mission)==0:
            showinfo('Error', 'You need to create a least 1 mission')
        else:
            folder = askdirectory()
            save_to_csv(liste_mission, liste_constellation, liste_gs, liste_poi, liste_satellite, folder)
            showinfo('Message', 'Simulation parameters saved')

    def load_simulation(self):
        self.reset()
        folder = askdirectory()
        er = import_from_csv(folder)
        for i in range(len(liste_gs)):
            gs_marker = self.__map_widget.set_marker(liste_gs[i].get_coordinate()[0], liste_gs[i].get_coordinate()[1], text=liste_gs[i].get_name(), marker_color_circle= "blue", marker_color_outside=liste_gs[i].get_color())
        for i in range(len(liste_poi)):
            if liste_poi[i].IsArea()== False:
                poi_marker = self.__map_widget.set_marker(liste_poi[i].get_coordinate(0)[0], liste_poi[i].get_coordinate(0)[1], text=liste_poi[i].get_name(), marker_color_circle= "yellow", marker_color_outside=liste_poi[i].get_color())
            else:
                if liste_poi[i].get_multi():
                    liste_poi[i].set_multipoly(liste_poi[i].get_area())
                    coords = liste_poi[i].get_area()
                    for j in range(len(coords)):
                        poly = self.__map_widget.set_polygon(coords[j], outline_color=liste_poi[i].get_color(), fill_color=liste_poi[i].get_color(), name=liste_poi[i].get_name())
                else:
                    poly = self.__map_widget.set_polygon(liste_poi[i].get_area(), outline_color=liste_poi[i].get_color(), fill_color=liste_poi[i].get_color(), name=liste_poi[i].get_name())
                self.grid_show_test(liste_poi[i].get_area())
                grid = self.grid_coords
                poly_grid = self.grid_poly
                liste_poi[i].set_grid(grid)
                liste_poi[i].set_poly(poly_grid)
                self.grid_coords = []
                self.grid_poly = []
        if er==0:
            showinfo("Message", "Simulation parameters loaded")
        else:
            showinfo("Message", "One or more file could not be loaded, it's recommended to reset the simulation or errors will be encoutered")

    def gs_visibility(self, miss, chosen_sat):
        time = []
        time_in_days = []
        visibility = []
        _, _, tf, dt = simulation_time(miss)
        for i in range(0, int(tf+dt), int(dt)):
            time.append(i)
        for j in range(len(time)):
                time_in_days.append(datetime.combine(miss.get_T0(), datetime.min.time()) + timedelta(seconds=int(time[j])))
        
        for i in range(int(miss.get_nb_gs())):
            
            gs_visiblity_interval = []
            date_ini_list = []
            timedelta_list = []
            fig2d = plt.figure(figsize=(10, 6))
            ax_2D = fig2d.add_subplot(211)
            gs = miss.get_gs(i)
            lat, long = gs.get_coordinate()
            alt = gs.get_altitude()
            ele = gs.get_elevation()
            ant = gs.get_antenna()
            band_att = get_attenuation(ele, gs.get_band(), lat, long, ant)
            gsx, gsy, gsz = latlong_to_cartesian(lat, long, alt)
            x, y, z = chosen_sat.get_position_ecef()
            interval, angle_list = gs_interval(x, y, z, lat, long, ele, gsx, gsy, gsz, dt, time)
            gs_visiblity_interval.append(interval)

            #Plot de l'angle d'élévation au cour du temps
            ax_2D.set_xlabel("Time (s)")
            ax_2D.set_ylabel("Elevation (°)")
            plt.title(f"Visibility from {gs.get_name()} of {chosen_sat.get_name()}")
            ax_2D.plot(time_in_days, angle_list, label=f"Elevation from {gs.get_name()}", color=chosen_sat.get_color())
            ax_2D.plot(time_in_days, np.full((len(time_in_days), 1), ele) , label=f"Minimum elevation ({ele}°) to be seen from {gs.get_name()}", color=gs.get_color())  
            ax_2D.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            for k in range(len(gs_visiblity_interval)):
                for j in range(len(gs_visiblity_interval[k])):
                    temp = gs_visiblity_interval[k][j]
                    date_ini = datetime.combine(miss.get_T0(), datetime.min.time()) + timedelta(seconds=int(temp[0]))
                    date_fin = datetime.combine(miss.get_T0(), datetime.min.time()) + timedelta(seconds=int(temp[1]))
                    date_ini_list.append(date_ini)
                    delta = date_fin - date_ini
                    timedelta_list.append(delta.seconds)
                    data_size = (gs.get_debit()*delta.seconds*eff_ini*band_att)/8
                    visibility.append((chosen_sat.get_name(), gs.get_name(), date_ini, date_fin, delta.seconds, data_size))
            #Plot les durées de visibilité
            ax_2D_2 = fig2d.add_subplot(212)
            ax_2D_2.bar([date.strftime('%Y-%m-%d %H:%M:%S') for date in date_ini_list], timedelta_list, width=0.35, color=list_colors, align='center')
            ax_2D_2.set_ylabel('Times (s)')
            ax_2D_2.legend()
            plt.title(f"Window opportunities duration at {gs.get_name()}")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            fig2d.savefig(result_folder / miss.get_name() / f"Result {gs.get_name()} visibility ({chosen_sat.get_name()}) figure.png")
        plt.show()
        save_gs_visibility(visibility, miss.get_name())

    def poi_visibility(self, miss, chosen_sat):
        time = []
        time_in_days = []
        visibility= []
        _, _, tf, dt = simulation_time(miss)
        for i in range(0, int(tf+dt), int(dt)):
            time.append(i)
        for j in range(len(time)):
                time_in_days.append(datetime.combine(miss.get_T0(), datetime.min.time()) + timedelta(seconds=int(time[j])))
        for i in range(int(miss.get_nb_poi())):
            poi_visiblity_interval = []
            date_ini_list = []
            timedelta_list = []
            poi = miss.get_poi(i)
            if poi.IsArea() == False:
                fig2d = plt.figure(figsize=(8, 10))
                ax_2D = fig2d.add_subplot(311)
                long = poi.get_coordinate(0)[1]
                lat =  poi.get_coordinate(0)[0]
                alt = poi.get_altitude()
                poix, poiy, poiz = latlong_to_cartesian(lat, long, alt)
                x, y, z = chosen_sat.get_position_ecef()
                swath = calcul_swath(chosen_sat)*1000
                interval, angle_list = poi_interval(x, y, z, lat, long, poix, poiy, poiz, swath, dt, time)
                poi_visiblity_interval.append(interval)

                #Plot de l'angle d'élévation au cour du temps
                ax_2D.set_xlabel("Time (UTC)")
                ax_2D.set_ylabel("Elevation (°)")
                ax_2D.plot(time_in_days, angle_list, label=f"Elevation from {poi.get_name()}", color=chosen_sat.get_color())
                ax_2D.legend()
                plt.title(f"Visibility from {poi.get_name()} of {chosen_sat.get_name()}")
                plt.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                zenith_angle, zenith_time = sun_zenith_angle(miss, lat, long, alt, poi.get_timezone(), poi.get_name())
                #Plot l'élévation du soleil sur le point d'interet au cour du temps
                ax_2D_2 = fig2d.add_subplot(312)
                ax_2D_2.plot(zenith_time, zenith_angle['elevation'], label='Sun zenith angle', color='blue')
                ax_2D_2.plot(time_in_days, np.full((len(time_in_days), 1), (float(miss.get_minsza()))) , label=f"Minimum sun elevation ({float(miss.get_minsza())}°) for the mission", color='black')
                ax_2D_2.set_xlabel('Times (UTC)')
                ax_2D_2.set_ylabel('Sun elevation angle (°)')
                ax_2D_2.legend()
                plt.title(f"Evolution of the sun elevation angle at {poi.get_name()}")
                plt.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                for k in range(len(poi_visiblity_interval)):
                    for j in range(len(poi_visiblity_interval[k])):
                        temp = poi_visiblity_interval[k][j]
                        date_ini = datetime.combine(miss.get_T0(), datetime.min.time()) + timedelta(seconds=int(temp[0]))
                        date_fin = datetime.combine(miss.get_T0(), datetime.min.time()) + timedelta(seconds=int(temp[1]))
                        date_ini_list.append(date_ini)
                        delta = date_fin - date_ini
                        timedelta_list.append(delta.seconds)
                        elevation_ini = zenith_angle.loc[date_ini.strftime("%Y-%m-%d %H:%M:%S")].elevation
                        elevation_fin = zenith_angle.loc[date_fin.strftime("%Y-%m-%d %H:%M:%S")].elevation
                        mean_elevation = (elevation_ini+elevation_fin)/2
                        visibility.append((chosen_sat.get_name(), poi.get_name(), date_ini, date_fin, delta.seconds, mean_elevation))
                sza_condition = []
                for i in range(len(visibility)):
                    if visibility[i][5] >= miss.get_minsza():
                        sza_condition.append(True)
                    else:
                        sza_condition.append(False)
                sza_color = ['green' if condition else 'red' for condition in sza_condition]
                #Plot les durées de visibilité
                ax_2D_3 = fig2d.add_subplot(313)
                ax_2D_3.bar([date.strftime('%Y-%m-%d %H:%M:%S') for date in date_ini_list], timedelta_list, width=0.35, color=sza_color, align='center')
                ax_2D_3.set_ylabel('Times (s)')
                legend_patches = [
                Patch(color='green', label=f'Date meeting SZA >= {miss.get_minsza()}'),
                Patch(color='red', label=f'Date not meeting SZA >= {miss.get_minsza()}')
                ]
                ax_2D_3.legend(handles=legend_patches)
                plt.title(f"Visibilities duration at {poi.get_name()} with a swath of {chosen_sat.get_swath()} km")
                plt.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()
                fig2d.savefig(result_folder / miss.get_name() / f"Result {poi.get_name()} visibility ({chosen_sat.get_name()}) figure.png")
                save_poi_visibility(visibility, miss.get_name())
            else:
                self.visibility_grid(poi, chosen_sat, miss)

                
        plt.show()

    def visibility_grid(self, poi, chosen_sat, miss):
        liste_centroid = []
        square_visible = []
        grid_poi = poi.get_grid()
        x, y, z = chosen_sat.get_position_ecef()
        swath = calcul_swath(chosen_sat)*1000
        if poi.get_multi():
            for i in range(len(grid_poi)):
                for square in grid_poi[i]:
                    liste_centroid.append(square.centroid)
        else:
            for square in grid_poi:
                liste_centroid.append(square.centroid)

        for i in range(len(liste_centroid)):
            long = liste_centroid[i].x
            lat = liste_centroid[i].y
            point = Point(long, lat)
            alt = poi.get_altitude()
            poix, poiy, poiz = latlong_to_cartesian(lat, long, alt)
            visible, sza = poi_grid(x, y, z, lat, long, poix, poiy, poiz, swath, miss, poi.get_timezone(), poi.get_name(), alt)
            square_visible.append((visible, sza, point))
        poi_poly = poi.get_poly()
        fig, ax = plt.subplots(figsize=(15, 15))
        if poi.get_multi():
            for i in range(len(grid_poi)):
                if grid_poi[i] == None:
                    pass
                else:
                    gpd.GeoSeries(grid_poi[i]).boundary.plot(ax=ax)
                    gpd.GeoSeries([poi_poly[i]]).boundary.plot(ax=ax,color="red")
        else:
            gpd.GeoSeries(grid_poi).boundary.plot(ax=ax)
            gpd.GeoSeries([poi_poly[0]]).boundary.plot(ax=ax,color="red")
        green = Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Observation possible')
        orange = Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Area visible but minimum sza not reached')
        red =Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Observation impossible')
        prct = 0
        for i in range(len(square_visible)):
            if square_visible[i][0]:
                if square_visible[i][1]:
                    gpd.GeoSeries(square_visible[i][2]).plot(ax=ax, color="green")
                    prct += 1
                else:
                    gpd.GeoSeries(square_visible[i][2]).plot(ax=ax, color="orange")
            else:
                gpd.GeoSeries(square_visible[i][2]).plot(ax=ax, color="red")
        ax.legend(handles=[green, orange, red])
        prct = (prct*100)/len(square_visible)
        plt.title(f"{prct:.2f}% of {poi.get_name()} covered during the simulation ")
        fig.savefig(result_folder / miss.get_name() / f"Result {poi.get_name()} visibility ({chosen_sat.get_name()}) figure.png")

    def save_result(self):
        for i in range(len(liste_mission)):
                if liste_mission[i].get_name()==str(self.combo_mission.get()):
                    mission = liste_mission[i]
        if mission == None:
            showinfo("Error", "Something went wrong ")
        else:
            time = []
            _, _, tf, dt = simulation_time(mission)
            for i in range(0, int(tf+dt), int(dt)):
                time.append(i)
            const = mission.get_constellation()
            poi = []
            poi_opportunities = []
            gs = []
            gs_opportunities = []
            sat = []
            for i in range(mission.get_nb_poi()):
                poi.append(mission.get_poi(i))
            for i in range(mission.get_nb_gs()):
                gs.append(mission.get_gs(i))
            for i in range(const.get_nb_sat_tot()):
                sat.append(const.get_sat(i))

            for i in range(len(poi)):
                poi_visibility = []
                liste_centroid = []
                grid_poi = poi[i].get_grid()
                alt = poi[i].get_altitude()
                if poi[i].IsArea():
                    if poi[i].get_multi():
                        for k in range(len(grid_poi)):
                            for square in grid_poi[k]:
                                liste_centroid.append(square.centroid)
                    else:
                        for square in grid_poi:
                            liste_centroid.append(square.centroid)
                else:
                    long = poi[i].get_coordinate(0)[1]
                    lat =  poi[i].get_coordinate(0)[0]

                for j in range(len(sat)):
                    x, y, z = sat[j].get_position_ecef()
                    swath = calcul_swath(sat[j])*1000
                    if poi[i].IsArea():
                        square_visible = []
                        for q in range(len(liste_centroid)):
                            long = liste_centroid[q].x
                            lat = liste_centroid[q].y
                            point = Point(long, lat)
                            poix, poiy, poiz = latlong_to_cartesian(lat, long, alt)
                            visible, sza = poi_grid(x, y, z, lat, long, poix, poiy, poiz, swath, mission, poi[i].get_timezone(), poi[i].get_name(), alt)
                            square_visible.append((visible, sza, point))
                        poi_visibility.append((True, square_visible, poi[i].get_poly(), grid_poi, poi[i].get_multi()))
                    else:
                        poix, poiy, poiz = latlong_to_cartesian(lat, long, alt)
                        interval, _ = poi_interval(x, y, z, lat, long, poix, poiy, poiz, swath, dt, time)
                        poi_visibility.append(( False, sat[j].get_name(), len(interval)))
                poi_opportunities.append((poi[i].get_name(), poi_visibility))
            
            for i in range(len(gs)):
                gs_visibility = []
                lat, long = gs[i].get_coordinate()
                alt = gs[i].get_altitude()
                ele = gs[i].get_elevation()
                gsx, gsy, gsz = latlong_to_cartesian(lat, long, alt)

                for j in range(len(sat)):
                    x, y, z = sat[j].get_position_ecef()
                    interval, _ = gs_interval(x, y, z, lat, long, ele, gsx, gsy, gsz, dt, time)
                    gs_visibility.append((sat[j].get_name(), len(interval)))
                gs_opportunities.append((gs[i].get_name(), gs_visibility))
            general_result(mission, gs_opportunities, poi_opportunities)
            showinfo("Message", "Mission report created successfully")

#############################################################################################
# Additional windows

class ModifySatelliteWindow:
    def __init__(self, showsatinfo):
        self.top = tk.Toplevel()
        self.frame = tk.Frame(self.top)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.showsatinfo = showsatinfo

        self.l_combo_sat =ttk.Label(self.frame, text="Choose a Satellite to modify : ")
        self.l_combo_sat.grid(row=0, column=0, sticky="w")
        self.combo_sat = ttk.Combobox(self.frame, postcommand= self.comb_sat_upd)
        self.combo_sat.grid(row=0, column=1, sticky="e")
        self.combo_sat['state'] = 'readonly'
        self.combo_sat.set('Choose a satellite...')

        ttk.Button(self.frame, text="Modify", command=self.submit).grid(row=1, column=1, pady=10)

    def comb_sat_upd(self):
        if len(liste_satellite)==0:
            self.combo_sat['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_satellite)):
                temp.append(liste_satellite[i].get_name())
            self.combo_sat['values'] = temp
    
    def submit(self):
        if (str(self.combo_sat.get()) == 'Choose a satellite...') or (str(self.combo_sat.get()) == 'Aucun'):
            showinfo("Error", "You need to choose a satellite !!!")
        else: 
            self.showsatinfo(self.combo_sat.get())
            self.top.destroy()

class ModifyConstellationWindow:
    def __init__(self, showconstinfo):
        self.top = tk.Toplevel()
        self.frame = tk.Frame(self.top)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.showconstinfo = showconstinfo

        self.l_combo_const =ttk.Label(self.frame, text="Choose a Constellation to modify : ")
        self.l_combo_const.grid(row=0, column=0, sticky="w")
        self.combo_const = ttk.Combobox(self.frame, postcommand= self.comb_const_upd)
        self.combo_const.grid(row=0, column=1, sticky="e")
        self.combo_const['state'] = 'readonly'
        self.combo_const.set('Choose a constellation...')

        ttk.Button(self.frame, text="Modify", command=self.submit).grid(row=1, column=1, pady=10)

    def comb_const_upd(self):
        if len(liste_constellation)==0:
            self.combo_const['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_constellation)):
                temp.append(liste_constellation[i].get_name())
            self.combo_const['values'] = temp
    
    def submit(self):
        if (str(self.combo_const.get()) == 'Choose a constellation...') or (str(self.combo_const.get()) == 'Aucun'):
            showinfo("Error", "You need to choose a constellation !!!")
        else: 
            self.showconstinfo(self.combo_const.get())
            self.top.destroy()

class ModifyGSWindow:
    def __init__(self, showgsinfo):
        self.top = tk.Toplevel()
        self.frame = tk.Frame(self.top)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.showgsinfo = showgsinfo

        self.l_combo_gs =ttk.Label(self.frame, text="Choose a Ground Station to modify : ")
        self.l_combo_gs.grid(row=0, column=0, sticky="w")
        self.combo_gs = ttk.Combobox(self.frame, postcommand= self.comb_gs_upd)
        self.combo_gs.grid(row=0, column=1, sticky="e")
        self.combo_gs['state'] = 'readonly'
        self.combo_gs.set('Choose a ground station...')

        ttk.Button(self.frame, text="Modify", command=self.submit).grid(row=1, column=1, pady=10)

    def comb_gs_upd(self):
        if len(liste_gs)==0:
            self.combo_gs['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_gs)):
                temp.append(liste_gs[i].get_name())
            self.combo_gs['values'] = temp
    
    def submit(self):
        if (str(self.combo_gs.get()) == 'Choose a ground station...') or (str(self.combo_gs.get()) == 'Aucun'):
            showinfo("Error", "You need to choose a groundstation !!!")
        else: 
            self.showgsinfo(self.combo_gs.get())
            self.top.destroy()

class ModifyPOIWindow:
    def __init__(self, showpoiinfo):
        self.top = tk.Toplevel()
        self.frame = tk.Frame(self.top)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.showpoiinfo = showpoiinfo

        self.l_combo_poi =ttk.Label(self.frame, text="Choose a Point of Interest to modify : ")
        self.l_combo_poi.grid(row=0, column=0, sticky="w")
        self.combo_poi = ttk.Combobox(self.frame, postcommand= self.comb_gs_upd)
        self.combo_poi.grid(row=0, column=1, sticky="e")
        self.combo_poi['state'] = 'readonly'
        self.combo_poi.set('Choose a point of interest...')

        ttk.Button(self.frame, text="Modify", command=self.submit).grid(row=1, column=1, pady=10)

    def comb_gs_upd(self):
        if len(liste_poi)==0:
            self.combo_poi['values'] = 'Aucun'
        else:
            temp = []
            for i in range(len(liste_poi)):
                if liste_poi[i].IsArea() == False:
                    temp.append(liste_poi[i].get_name())
            self.combo_poi['values'] = temp
    
    def submit(self):
        if (str(self.combo_poi.get()) == 'Choose a point of interest...') or (str(self.combo_poi.get()) == 'Aucun'):
            showinfo("Error", "You need to choose a point of interest !!!")
        else: 
            self.showpoiinfo(self.combo_poi.get())
            self.top.destroy()

class FetchTLEWindow:
    def __init__(self, fetchtle):
        self.top = tk.Toplevel()
        self.frame = tk.Frame(self.top)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.fetchtle = fetchtle

        self.l_noradID =ttk.Label(self.frame, text="Enter the NORAD ID of the satellite : ")
        self.l_noradID.grid(row=0, column=0, sticky="w")
        self.noradID = ttk.Entry(self.frame)
        self.noradID.grid(row=0, column=1, sticky="e")

        ttk.Button(self.frame, text="Search", command=self.submit).grid(row=1, column=1, pady=10)
    
    def submit(self):
        try:
            float(self.noradID.get())
            self.fetchtle(float(self.noradID.get()))
            self.top.destroy()
        except ValueError:
            showinfo("Error", "You need to enter a correct NORAD ID !!!")

class ChooseResolutionWindow:
    def __init__(self, chooseres):
        self.top = tk.Toplevel()
        self.frame = tk.Frame(self.top)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.chooseres = chooseres

        self.l_res =ttk.Label(self.frame, text="Choose the mesh resolution  : ")
        self.l_res.grid(row=0, column=0, sticky="w")
        self.res = tk.StringVar()
        self.res.set("50")

        self.res1 = ttk.Radiobutton(self.frame, text="1:10 m", variable=self.res, value="10").grid(row=1, column=0, pady=10)
        self.res2 = ttk.Radiobutton(self.frame, text="1:50 m", variable=self.res, value="50").grid(row=1, column=1, pady=10)
        self.res3 = ttk.Radiobutton(self.frame, text="1:110 m", variable=self.res, value="110").grid(row=1, column=2, pady=10)

        ttk.Button(self.frame, text="Launch", command=self.submit).grid(row=2, column=1, pady=10)

    def submit(self):
            self.chooseres(str(self.res.get()))
            self.top.destroy()

class ResultChoiceWindow:
    def __init__(self, gs_visibility, poi_visibility, miss, chosen_sat):
        self.top = tk.Toplevel()
        self.frame = tk.Frame(self.top)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.gs_visibility = gs_visibility
        self.poi_visibility = poi_visibility
        self.miss = miss
        self.chosen_sat = chosen_sat

        self.l_choice =ttk.Label(self.frame, text="Choose a result  : ")
        self.l_choice.grid(row=0, column=0, sticky="w")
        
        self.l_gs_visibility = ttk.Label(self.frame, text='Visibility from Ground Stations')
        self.l_gs_visibility.grid(row=1, column=0, sticky="w")
        ttk.Button(self.frame, text='Show', command=self.gs).grid(row=1, column=1, sticky="w")

        self.l_poi_visibility = ttk.Label(self.frame, text='Visibility of POIs')
        self.l_poi_visibility.grid(row=2, column=0, sticky="w")
        ttk.Button(self.frame, text='Show', command=self.poi).grid(row=2, column=1, sticky="w")

    def gs(self):
        self.gs_visibility(self.miss, self.chosen_sat)
    def poi(self):
        self.poi_visibility(self.miss, self.chosen_sat)