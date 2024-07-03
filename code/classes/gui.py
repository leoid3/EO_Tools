import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs
import tkintermapview as tkmap
from config import *
from functions.initialisation import init_constellation, init_poi, init_gs, init_mission, init_sat, init_orb
from functions.calcul import calcul_traj
from functions.save_data import save_to_csv
from functions.import_data import import_from_csv

class SatelliteSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.marker_list=[]
        self.title("EO Tools")
        self.geometry("")

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
        map_frame.place(relx = 0.49, rely= 0, anchor="n")
        """
        self.__map_widget = tkmap.TkinterMapView(map_frame, width = 690, height = 690, corner_radius = 0)
        #self.__map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.__map_widget.place(relx = 0.5, rely=0.5, anchor= tk.CENTER)
        self.__map_widget.set_position(48.860381, 2.338594)  # Paris, France
        self.__map_widget.set_zoom(5)
        self.__map_widget.pack()
        """
        self.fig3d = plt.figure()
        self.ax_3D = self.fig3d.add_subplot(111, projection='3d')
        self.ax_3D.plot([0], [0], [0], 'o', label='Terre', markersize=12)

        self.canvas3d = FigureCanvasTkAgg(self.fig3d, master=map_frame)
        self.canvas3d.draw()
        self.canvas3d.get_tk_widget().grid(row=0, column=2, rowspan=2, padx=10, pady=10)
        

        # Frame for 2D trace visualization
        self.fig2d = plt.figure()
        self.ax_2D = self.fig2d.add_subplot(111, projection=ccrs.PlateCarree())
        self.ax_2D.stock_img()

        self.canvas2d = FigureCanvasTkAgg(self.fig2d, master=map_frame)
        self.canvas2d.draw()
        self.canvas2d.get_tk_widget().grid(row=2, column=2, columnspan=3, padx=10, pady=10)

    def tab1(self):
        # Frame for the satellite tab
        sat_frame = ttk.LabelFrame(self.main_frame, text="Satellite Creation :", padding=(10, 10))
        #sat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        sat_frame.place(relx= 0.1, rely=0, anchor= "n")

        self.l_sn = ttk.Label(sat_frame, text="Name of the Satellite : ")
        self.l_sn.grid(row=0, column=0, sticky="w")
        self.sat_name = ttk.Entry(sat_frame)
        self.sat_name.grid(row=0, column=1, sticky="e")

        self.l_sw = ttk.Label(sat_frame, text="Swath (km) : ")
        self.l_sw.grid(row=1, column=0, sticky="w")
        self.sat_swath = ttk.Entry(sat_frame)
        self.sat_swath.grid(row=1, column=1, sticky="e")

        self.l_dep = ttk.Label(sat_frame, text="Depointing (°) : ")
        self.l_dep.grid(row=2, column=0, sticky="w")
        self.sat_dep = ttk.Entry(sat_frame)
        self.sat_dep.grid(row=2, column=1, sticky="e")

        ttk.Label(sat_frame, text="Color : ").grid(row=3, column=0, sticky="w")
        self.combo_color = ttk.Combobox(sat_frame)
        self.combo_color.grid(row=3, column=1, sticky="e")
        self.combo_color['state'] = 'readonly'
        self.combo_color.set(list_colors[0])
        self.combo_color['values'] = list_colors
        

        ttk.Label(sat_frame, text="Type : ").grid(row=4, column=0, sticky="w")
        self.combo_type = ttk.Combobox(sat_frame)
        self.combo_type.grid(row=4, column=1, sticky="e")
        self.combo_type['state'] = 'readonly'
        self.combo_type.set(sat_type[0])
        self.combo_type['values'] = sat_type

        # Frame for the orbit
        #orb_frame = ttk.LabelFrame(self, text="Orbit Creation :", padding=(10, 10))
        #orb_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(sat_frame, text='Orbit Creation :').grid(row=5, column=0, padx=10, pady=10, sticky="nw")
        self.l_a =ttk.Label(sat_frame, text="Altitude (km):")
        self.l_a.grid(row=6, column=0, sticky="w")
        self.altitude = ttk.Entry(sat_frame)
        self.altitude.grid(row=6, column=1, sticky="e")

        self.l_e = ttk.Label(sat_frame, text="Eccentricity:")
        self.l_e.grid(row=7, column=0, sticky="w")
        self.eccentricity = ttk.Entry(sat_frame)
        self.eccentricity.grid(row=7, column=1, sticky="e")

        self.l_i = ttk.Label(sat_frame, text="Inclination (°):")
        self.l_i.grid(row=8, column=0, sticky="w")
        self.inclination = ttk.Entry(sat_frame)
        self.inclination.grid(row=8, column=1, sticky="e")

        self.l_raan = ttk.Label(sat_frame, text="RAAN (°):")
        self.l_raan.grid(row=9, column=0, sticky="w")
        self.raan = ttk.Entry(sat_frame)
        self.raan.grid(row=9, column=1, sticky="e")

        self.l_ap = ttk.Label(sat_frame, text="Argument of Perigee (°):")
        self.l_ap.grid(row=10, column=0, sticky="w")
        self.arg_perigee = ttk.Entry(sat_frame)
        self.arg_perigee.grid(row=10, column=1, sticky="e")

        self.l_ta = ttk.Label(sat_frame, text="True Anomaly (°):")
        self.l_ta.grid(row=11, column=0, sticky="w")
        self.true_anomaly = ttk.Entry(sat_frame)
        self.true_anomaly.grid(row=11, column=1, sticky="e")

        ttk.Button(sat_frame, text="Add Satellite", command=self.add_satellite).grid(row=12, column=0, columnspan=2, pady=10)

    def tab2(self):
        const_frame = ttk.LabelFrame(self.main_frame, text="Constellation Creation :", padding=(10, 10))
        #const_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        const_frame.place(relx= 0.117, rely=0.45, anchor= "n")

        self.l_consn = ttk.Label(const_frame, text="Name of the Constellation : ")
        self.l_consn.grid(row=0, column=0, sticky="w")
        self.const_name = ttk.Entry(const_frame)
        self.const_name.grid(row=0, column=1, sticky="e")

        ttk.Label(const_frame, text="Walker Constellation Parameters : ").grid(row=1, column=0, sticky="w")
        self.l_walkerT = ttk.Label(const_frame, text="Number of total Satellite : ")
        self.l_walkerT.grid(row=2, column=0, sticky="w")
        self.walkerT = ttk.Entry(const_frame)
        self.walkerT.grid(row=2, column=1, sticky="e")

        self.l_walkerP = ttk.Label(const_frame, text="Number of orbital plane : ")
        self.l_walkerP.grid(row=3, column=0, sticky="w")
        self.walkerP = ttk.Entry(const_frame)
        self.walkerP.grid(row=3, column=1, sticky="e")

        self.l_walkerF = ttk.Label(const_frame, text="Phasing factor : ")
        self.l_walkerF.grid(row=4, column=0, sticky="w")
        self.walkerF = ttk.Entry(const_frame)
        self.walkerF.grid(row=4, column=1, sticky="e")

        self.l_combo_sat =ttk.Label(const_frame, text="Choose a Satellite's model : ")
        self.l_combo_sat.grid(row=5, column=0, sticky="w")
        self.combo_sat = ttk.Combobox(const_frame, postcommand= self.comb_sat_upd)
        self.combo_sat.grid(row=5, column=1, sticky="e")
        self.combo_sat['state'] = 'readonly'
        self.combo_sat.set('Choose a model...')

        ttk.Label(const_frame, text="Color : ").grid(row=6, column=0, sticky="w")
        self.combo_color_const = ttk.Combobox(const_frame)
        self.combo_color_const.grid(row=6, column=1, sticky="e")
        self.combo_color_const['state'] = 'readonly'
        self.combo_color_const.set(list_colors[0])
        self.combo_color_const['values'] = list_colors

        ttk.Button(const_frame, text="Add Constellation", command=self.add_constellation).grid(row=7, column=0, columnspan=2, pady=10)

    def tab3(self):
        poi_frame = ttk.LabelFrame(self.main_frame, text="Point of Interest Creation :", padding=(10, 10))
        #poi_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nw")
        poi_frame.place(relx= 0.73, rely=0)

        self.l_poin = ttk.Label(poi_frame, text="Name of the POI : ")
        self.l_poin.grid(row=0, column=0, sticky="w")
        self.poi_name = ttk.Entry(poi_frame)
        self.poi_name.grid(row=0, column=1, sticky="e")

        self.l_lat = ttk.Label(poi_frame, text="Latitude (DD) : ")
        self.l_lat.grid(row=1, column=0, sticky="w")
        self.poi_lat = ttk.Entry(poi_frame)
        self.poi_lat.grid(row=1, column=1, sticky="e")

        self.l_long = ttk.Label(poi_frame, text="Longitude (DD) : ")
        self.l_long.grid(row=2, column=0, sticky="w")
        self.poi_long = ttk.Entry(poi_frame)
        self.poi_long.grid(row=2, column=1, sticky="e")

        self.l_alt = ttk.Label(poi_frame, text="Altitude (m) : ")
        self.l_alt.grid(row=3, column=0, sticky="w")
        self.poi_alt = ttk.Entry(poi_frame)
        self.poi_alt.grid(row=3, column=1, sticky="e")

        ttk.Label(poi_frame, text="Color : ").grid(row=4, column=0, sticky="w")
        self.combo_color_poi = ttk.Combobox(poi_frame)
        self.combo_color_poi.grid(row=4, column=1, sticky="e")
        self.combo_color_poi['state'] = 'readonly'
        self.combo_color_poi.set(list_colors[0])
        self.combo_color_poi['values'] = list_colors

        ttk.Button(poi_frame, text="Add POI", command=self.add_poi).grid(row=5, column=0, columnspan=2, pady=10)

        self.l_gsn = ttk.Label(poi_frame, text="Name of the Ground Station : ")
        self.l_gsn.grid(row=6, column=0, sticky="w")
        self.gs_name = ttk.Entry(poi_frame)
        self.gs_name.grid(row=7, column=1, sticky="e")

        self.l_gslat = ttk.Label(poi_frame, text="Latitude (DD) : ")
        self.l_gslat.grid(row=8, column=0, sticky="w")
        self.gs_lat = ttk.Entry(poi_frame)
        self.gs_lat.grid(row=9, column=1, sticky="e")

        self.l_gslong = ttk.Label(poi_frame, text="Longitude (DD) : ")
        self.l_gslong.grid(row=10, column=0, sticky="w")
        self.gs_long = ttk.Entry(poi_frame)
        self.gs_long.grid(row=11, column=1, sticky="e")

        self.l_gsalt = ttk.Label(poi_frame, text="Altitude (m) : ")
        self.l_gsalt.grid(row=12, column=0, sticky="w")
        self.gs_alt = ttk.Entry(poi_frame)
        self.gs_alt.grid(row=12, column=1, sticky="e")

        self.l_gsel = ttk.Label(poi_frame, text="Elevation (°) : ")
        self.l_gsel.grid(row=13, column=0, sticky="w")
        self.gs_ele = ttk.Entry(poi_frame)
        self.gs_ele.grid(row=13, column=1, sticky="e")

        self.l_gsbw = ttk.Label(poi_frame, text="Bandwith (Mhz) : ")
        self.l_gsbw.grid(row=14, column=0, sticky="w")
        self.gs_bw = ttk.Entry(poi_frame)
        self.gs_bw.grid(row=14, column=1, sticky="e")

        self.l_gsdeb = ttk.Label(poi_frame, text="Debit (Mb/s) : ")
        self.l_gsdeb.grid(row=15, column=0, sticky="w")
        self.gs_deb = ttk.Entry(poi_frame)
        self.gs_deb.grid(row=15, column=1, sticky="e")

        ttk.Label(poi_frame, text="Color : ").grid(row=16, column=0, sticky="w")
        self.combo_color_gs = ttk.Combobox(poi_frame)
        self.combo_color_gs.grid(row=16, column=1, sticky="e")
        self.combo_color_gs['state'] = 'readonly'
        self.combo_color_gs.set(list_colors[0])
        self.combo_color_gs['values'] = list_colors

        ttk.Button(poi_frame, text="Add Ground Station", command=self.add_gs).grid(row=17, column=0, columnspan=2, pady=10)    

    def tab5(self):

        self.__poi_temp = []
        self.__gs_temp = []
        self.mission_frame = ttk.LabelFrame(self.main_frame, text="Mission Creation :", padding=(10, 10),)
        #self.mission_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        self.mission_frame.place(relx=0.73, rely=0.57)

        self.l_mn = ttk.Label(self.mission_frame, text="Name of the Mission : ")
        self.l_mn.grid(row=0, column=0, sticky="w")
        self.mission_name = ttk.Entry(self.mission_frame)
        self.mission_name.grid(row=0, column=1, sticky="e")

        self.l_misstime = ttk.Label(self.mission_frame, text="Duration of the mission (s) : ")
        self.l_misstime.grid(row=1, column=0, sticky="w")
        self.mission_time = ttk.Entry(self.mission_frame)
        self.mission_time.grid(row=1, column=1, sticky="e")

        self.l_timestep = ttk.Label(self.mission_frame, text="Time step of the mission (s) : ")
        self.l_timestep.grid(row=2, column=0, sticky="w")
        self.timestep = ttk.Entry(self.mission_frame)
        self.timestep.grid(row=2, column=1, sticky="e")

        ttk.Label(self.mission_frame, text="Type : ").grid(row=3, column=0, sticky="w")
        self.combo_mission_type = ttk.Combobox(self.mission_frame)
        self.combo_mission_type.grid(row=3, column=1, sticky="e")
        self.combo_mission_type['state'] = 'readonly'
        self.combo_mission_type.set(sat_type[0])
        self.combo_mission_type['values'] = sat_type

        self.l_sza = ttk.Label(self.mission_frame, text="Minimun Sun Zenith Angle (°) : ")
        self.l_sza.grid(row=4, column=0, sticky="w")
        self.minsza = ttk.Entry(self.mission_frame)
        self.minsza.grid(row=4, column=1, sticky="e")

        self.l_combo_poi = ttk.Label(self.mission_frame, text="Poi : ")
        self.l_combo_poi.grid(row=5, column=0, sticky="w")
        self.combo_poi = ttk.Combobox(self.mission_frame, postcommand= self.comb_poi_upd)
        self.combo_poi.grid(row=5, column=1, sticky="e")
        self.combo_poi['state'] = 'readonly'
        self.combo_poi.set('Choose a POI...')

        self.l_combo_gs = ttk.Label(self.mission_frame, text="GS : ")
        self.l_combo_gs.grid(row=6, column=0, sticky="w")
        self.combo_gs = ttk.Combobox(self.mission_frame, postcommand= self.comb_gs_upd)
        self.combo_gs.grid(row=6, column=1, sticky="e")
        self.combo_gs['state'] = 'readonly'
        self.combo_gs.set('Choose a GS...')

        self.l_combo_const = ttk.Label(self.mission_frame, text="Constellation : ")
        self.l_combo_const.grid(row=7, column=0, sticky="w")
        self.combo_const = ttk.Combobox(self.mission_frame, postcommand= self.comb_const_upd)
        self.combo_const.grid(row=7, column=1, sticky="e")
        self.combo_const['state'] = 'readonly'
        self.combo_const.set('Choose a Constellation...')

        ttk.Button(self.mission_frame, text="Add Mission", command=self.add_mission).grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(self.mission_frame, text="Associate", command=self.ass_gs_mission).grid(row=6, column=2, columnspan=2, pady=10)
        ttk.Button(self.mission_frame, text="Associate", command=self.ass_poi_mission).grid(row=5, column=2, columnspan=2, pady=10)

    def tab6(self):
        # Frame for simulation control
        control_frame = ttk.LabelFrame(self.main_frame, text="Simulation :", padding=(10, 10))
        
        control_frame.place(relx =0.38, rely= 0.88)

        ttk.Label(control_frame, text="Mission : ").grid(row=0, column=1, sticky="w")
        self.combo_mission = ttk.Combobox(control_frame, postcommand= self.comb_miss_upd)
        self.combo_mission.grid(row=0, column=1, sticky="e")
        self.combo_mission['state'] = 'readonly'
        self.combo_mission.set('Choose a Mission...')

        ttk.Button(control_frame, text="Run Simulation", command=self.run_simulation).grid(row=1, column=0, pady=5)
        ttk.Button(control_frame, text="Save Simulation", command=self.save_simulation).grid(row=1, column=1, pady=5)
        ttk.Button(control_frame, text="Load Simulation", command=self.load_simulation).grid(row=1, column=2, pady=5)
        ttk.Button(control_frame, text="Reset", command=self.reset).grid(row=1, column=3, pady=5)
       
    def add_satellite(self):
        i=0
        if self.validate_entry(self.altitude.get()) == False:
            self.l_a.config(foreground = "red")
            i=+1
        else:
            self.l_a.config(foreground = "green")
        if self.validate_entry(self.eccentricity.get())== False:
            self.l_e.config(foreground = "red")
            i=+1
        else:
            self.l_e.config(foreground = "green")
        if self.validate_entry(self.inclination.get())== False:
            self.l_i.config(foreground = "red")
            i=+1
        else:
            self.l_i.config(foreground = "green")
        if self.validate_entry(self.raan.get())== False:
            self.l_raan.config(foreground = "red")
            i=+1
        else:
            self.l_raan.config(foreground = "green")
        if self.validate_entry(self.arg_perigee.get())== False:
            self.l_ap.config(foreground = "red")
            i=+1
        else:
            self.l_ap.config(foreground = "green")
        if self.validate_entry(self.true_anomaly.get())== False:
            self.l_ta.config(foreground = "red")
            i=+1
        else:
            self.l_ta.config(foreground = "green")

        if self.validate_entry(self.sat_swath.get())== False:
            self.l_sw.config(foreground = "red")
            i=+1
        else:
            self.l_sw.config(foreground = "green")

        if self.validate_entry(self.sat_dep.get())== False:
            self.l_dep.config(foreground = "red")
            i=+1
        else:
            self.l_dep.config(foreground = "green")
        if len(self.sat_name.get())== 0:
            self.l_sn.config(foreground = "red")
            i=+1
        else:
            self.l_sn.config(foreground = "green")
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
            showinfo("Message", "Satellite ajouté avec succès !")
        else:
            showinfo("Error", "Un ou plusieurs parametre sont manquants")

    def add_constellation(self):
        i=0
        if self.validate_entry(self.walkerP.get()) == False:
            self.l_walkerP.config(foreground = "red")
            i=+1
        else:
            self.l_walkerP.config(foreground = "green")
        if self.validate_entry(self.walkerF.get())== False:
            self.l_walkerF.config(foreground = "red")
            i=+1
        else:
            self.l_walkerF.config(foreground = "green")
        if self.validate_entry(self.walkerT.get())== False:
            self.l_walkerT.config(foreground = "red")
            i=+1
        else:
            self.l_walkerT.config(foreground = "green")
        if len(self.const_name.get())== 0:
            self.l_consn.config(foreground = "red")
            i=+1
        else:
            self.l_consn.config(foreground = "green")
        if (str(self.combo_sat.get()) == 'Choose a model...') or (str(self.combo_sat.get()) == 'Aucun'):
            print("You need to choose a model !!!")
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
                    showinfo("Message", "Constellation ajoutée avec succès !")
        else:
            showinfo("Error", "Un ou plusieurs parametre sont manquants")

    def add_poi(self):
        i=0
        if self.validate_entry(self.poi_alt.get()) == False:
            self.l_alt.config(foreground = "red")
            i=+1
        else:
            self.l_alt.config(foreground = "green")
        if self.validate_entry(self.poi_long.get())== False:
            self.l_long.config(foreground = "red")
            i=+1
        else:
            self.l_long.config(foreground = "green")
        if self.validate_entry(self.poi_lat.get())== False:
            self.l_lat.config(foreground = "red")
            i=+1
        else:
            self.l_lat.config(foreground = "green")
        if len(self.poi_name.get())== 0:
            self.l_poin.config(foreground = "red")
            i=+1
        else:
            self.l_poin.config(foreground = "green")

        if i==0:
            poi = init_poi(str(self.poi_name.get()),
                           float(self.poi_long.get()),
                           float(self.poi_lat.get()),
                           float(self.poi_alt.get()),
                           str(self.combo_color_poi.get()))
            liste_poi.append(poi)
            self.ax_2D.plot(poi.get_coordinate(0)[1], poi.get_coordinate(0)[0], 'x', label=poi.get_name(), color=poi.get_color())
            self.ax_2D.legend()
            self.canvas2d.draw()
            showinfo("Message", "POI ajouté avec succès")
        else:
            showinfo("Error", "Un ou plusieurs parametres sont manquants")

    def add_gs(self):
        i=0
        if self.validate_entry(self.gs_alt.get()) == False:
            self.l_gsalt.config(foreground = "red")
            i=+1
        else:
            self.l_gsalt.config(foreground = "green")
        if self.validate_entry(self.gs_long.get())== False:
            self.l_gslong.config(foreground = "red")
            i=+1
        else:
            self.l_gslong.config(foreground = "green")
        if self.validate_entry(self.gs_lat.get())== False:
            self.l_gslat.config(foreground = "red")
            i=+1
        else:
            self.l_gslat.config(foreground = "green")
        if self.validate_entry(self.gs_lat.get())== False:
            self.l_gslat.config(foreground = "red")
            i=+1
        else:
            self.l_gslat.config(foreground = "green")
        if self.validate_entry(self.gs_ele.get())== False:
            self.l_gsel.config(foreground = "red")
            i=+1
        else:
            self.l_gsel.config(foreground = "green")
        
        if self.validate_entry(self.gs_bw.get())== False:
            self.l_gsbw.config(foreground = "red")
            i=+1
        else:
            self.l_gsbw.config(foreground = "green")
        if self.validate_entry(self.gs_deb.get())== False:
            self.l_gsdeb.config(foreground = "red")
            i=+1
        else:
            self.l_gsdeb.config(foreground = "green")

        if len(self.gs_name.get())== 0:
            self.l_gsn.config(foreground = "red")
            i=+1
        else:
            self.l_gsn.config(foreground = "green")

        if i==0:
            gs = init_gs( str(self.gs_name.get()),
                           float(self.gs_long.get()),
                           float(self.gs_lat.get()),
                           float(self.gs_alt.get()),
                           float(self.gs_ele.get()),
                           float(self.gs_bw.get()),
                           float(self.gs_deb.get()),
                           str(self.combo_color_gs.get()))
            liste_gs.append(gs)
            print("Ground Station ajoutée avec succes")
            self.ax_2D.plot(gs.get_coordinate()[1], gs.get_coordinate()[0], 'o', label=gs.get_name(), color=gs.get_color())
            self.ax_2D.legend()
            self.canvas2d.draw()
            showinfo("Message", "GS ajouté avec succès !")
        else:
            showinfo("Error", "Un ou plusieurs parametre sont manquants")

    def add_mission(self):
        i=0
        if self.validate_entry(self.mission_time.get()) == False:
            self.l_misstime.config(foreground = "red")
            i=+1
        else:
            self.l_misstime.config(foreground = "green")
        if self.validate_entry(self.timestep.get()) == False:
            self.l_timestep.config(foreground = "red")
            i=+1
        else:
            self.l_timestep.config(foreground = "green")
        if self.validate_entry(self.minsza.get()) == False:
            self.l_sza.config(foreground = "red")
            i=+1
        else:
            self.l_sza.config(foreground = "green")
        if (str(self.combo_const.get()) == 'Choose a Constellation...') or (str(self.combo_const.get()) == 'Aucun'):
            self.l_combo_const.config(foreground = "red")
            i=+1
        else:
            self.l_combo_const.config(foreground = "green")
        if len(self.mission_name.get())== 0:
            self.l_mn.config(foreground = "red")
            i=+1
        else:
            self.l_mn.config(foreground = "green")
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
                                   float(self.mission_time.get()),
                                   str(self.combo_mission_type.get()),
                                   float(self.minsza.get()),
                                   self.__poi_temp,
                                   self.__gs_temp,
                                   str(self.combo_const.get()))
            liste_mission.append(mission)
            showinfo("Message", "Mission ajoutée avec succès")
        else:
            showinfo("Error", "Un ou plusieurs parametre sont manquants")
 
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
            showinfo("Error", "You need to create a mission to continue")
        else:
            for i in range(len(liste_mission)):
                if liste_mission[i].get_name()==str(self.combo_mission.get()):
                    calcul_traj(liste_mission[i], self.ax_3D, self.ax_2D)
            self.canvas2d.draw()
            self.canvas3d.draw()
            showinfo("Message", "Simulation simulated correctly")
                              
    def reset(self):
        self.ax_2D.clear()
        self.ax_3D.clear()
        self.map_tab()
        self.tab6()
        showinfo("Message", "Simulation reseted")

    def save_simulation(self):
        # Placeholder for save logic
        if len(liste_mission)==0:
            showinfo('Error', 'You need to create a least 1 mission')
        else:
            save_to_csv(liste_mission, liste_constellation, liste_gs, liste_poi, liste_satellite)
            showinfo('Message', 'Saved')

    def load_simulation(self):
        import_from_csv()
        showinfo("Message", "Simulation loaded")