# ---------------------------------------------------------------
# Classes for the creation of the GUI for the Traffic Model creation.
# Map-user interactions are defined, as well as the terminal type
# creation and placement interfaces.
#
# (C) 2024 César Leal-Graciani Mena, Toulouse, France
# email leal@satconsult.eu
# ---------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, simpledialog
from tkintermapview import TkinterMapView
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
import time
from scipy.interpolate import RegularGridInterpolator
from scipy import interpolate
import pandas as pd
from tkinter.filedialog import askopenfilename
import os


class MapApplication:
    def __init__(self, root):
        self.root = root
        self.world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        self.terminal_distribution = None

        self.map_frame = ttk.Frame(root)
        self.map_frame.place(relx=0.79, rely=0.01, relwidth=0.58, relheight=0.7, anchor=tk.NE)
        self.map_widget = TkinterMapView(self.map_frame, width=self.map_frame.winfo_width(),
                                         height=self.map_frame.winfo_width())
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        self.map_widget.set_position(20, 0)
        self.map_widget.set_zoom(1)

        # Variables to keep track of the state
        self.country_selection_mode = False
        self.manual_polygon_mode = False
        self.manual_polygon_coords = []
        self.manual_paths = []
        self.selected_countries = []  # Contains the names of the selected countries
        self.selected_polygons = []  # Contains coordinates of the selected areas
        self.confirmed_polygons = []  # Contains coordinates of the confirmed areas
        self.selected_figures = []  # Contains the figures of the selected areas
        self.confirmed_figures = []  # Contains the figures of the confirmed areas
        self.terminals_coords = []  # Contains the coordinates of the placed terminals
        self.terminals_figures = []  # Contains the figures for the terminals
        self.saved_configs = []  # Contains saved configurations as a dictionary with coordinates for area and terminals
        self.saved_config_markers = []  # Contains the markers of the terminals in the saved selection
        self.saved_config_figures = []  # Contains the figures of the areas in the saved configurations

        # Flag to number polygons
        self.flag = 0

        # Name for the Traffic_Model excel File
        self.excel_name = ""

        # Initialisation of widgets
        self.separator = ttk.Separator(self.root, orient='vertical')
        self.instruction_label = tk.Label(self.root, text="", anchor="w", justify="left")
        self.countries_listbox = tk.Listbox(self.root, selectmode="single")
        self.confirmed_area_listbox = tk.Listbox(self.root, selectmode="single")
        self.saved_configurations_listbox = tk.Listbox(self.root, selectmode="single")

        # Obtain population density distribution
        file_path = 'Core/Data/glds15ag15.asc'
        self.popu_data, self.popu_ncols, self.popu_nrows, self.popu_xllcorner, self.popu_yllcorner, self.popu_cellsize,\
            self.popu_nodata_value = self.read_asc(file_path)

        self.long_grid = np.linspace(-180, 180, self.popu_data.shape[1])
        self.long_grid_index = np.arange(0, self.popu_data.shape[1])
        self.lat_grid = np.linspace(90, -90, self.popu_data.shape[0])
        self.lat_grid_index = np.arange(0, self.popu_data.shape[0])

        self.interpolator = RegularGridInterpolator((self.lat_grid, self.long_grid), self.popu_data)
        self.f_long = interpolate.interp1d(self.long_grid, self.long_grid_index)
        self.f_lat = interpolate.interp1d(self.lat_grid, self.lat_grid_index)

        self.config_index = -1  # Index for selected saved configuration
        # Add buttons, labels and listboxes
        self.create_widgets()

    def create_widgets(self):
        # SEPARATOR
        self.separator.place(relx=0.8, rely=0, relwidth=0.01, relheight=1)
        #######################################################################################################
        # Create a label for messages
        self.instruction_label.place(relx=0.214, rely=0.72, anchor=tk.NW)
        # Create a label for selected countries
        countries_list_title = tk.Label(self.root, text="Selected countries: ", anchor="w", justify="left")
        countries_list_title.place(relx=0.217, rely=0.75, anchor=tk.NW)
        # Create a label for confirmed area
        confirmed_area_list_title = tk.Label(self.root, text="Confirmed placement area: ", anchor="w", justify="left")
        confirmed_area_list_title.place(relx=0.364, rely=0.75, anchor=tk.NW)
        # Create a label for saved configurations
        saved_configurations_list_title = tk.Label(self.root, text="Saved configurations: ", anchor="w", justify="left")
        saved_configurations_list_title.place(relx=0.51, rely=0.75, anchor=tk.NW)

        # Create ListBox for selected countries
        self.countries_listbox.place(relx=0.22, rely=0.79, relwidth=0.12, relheight=0.18, anchor=tk.NW)
        # Create a scrollbar for the selected countries ListBox
        countries_scrollbar = tk.Scrollbar(self.root, orient="vertical")
        countries_scrollbar.place(relx=0.34, rely=0.79, relheight=0.18, anchor=tk.NW)
        self.countries_listbox.config(yscrollcommand=countries_scrollbar.set)
        countries_scrollbar.config(command=self.countries_listbox.yview)

        # Create ListBox for confirmed areas
        self.confirmed_area_listbox.place(relx=0.367, rely=0.79, relwidth=0.12, relheight=0.18, anchor=tk.NW)
        # Create a scrollbar for the confirmed countries ListBox
        confirmed_area_scrollbar = tk.Scrollbar(self.root, orient="vertical")
        confirmed_area_scrollbar.place(relx=0.487, rely=0.79, relheight=0.18, anchor=tk.NW)
        self.confirmed_area_listbox.config(yscrollcommand=confirmed_area_scrollbar.set)
        confirmed_area_scrollbar.config(command=self.confirmed_area_listbox.yview)

        # Create ListBox for saved configurations
        self.saved_configurations_listbox.place(relx=0.513, rely=0.79, relwidth=0.12, relheight=0.18, anchor=tk.NW)
        # Create a scrollbar for the manual selection ListBox
        saved_configurations_scrollbar = tk.Scrollbar(self.root, orient="vertical")
        saved_configurations_scrollbar.place(relx=0.633, rely=0.79, relheight=0.18, anchor=tk.NW)
        self.saved_configurations_listbox.config(yscrollcommand=saved_configurations_scrollbar.set)
        saved_configurations_scrollbar.config(command=self.saved_configurations_listbox.yview)
        # Attach event handler to the ListBox
        self.saved_configurations_listbox.bind("<<ListboxSelect>>", self.show_saved_configuration)

        # Create map's buttons
        add_country_button = ttk.Button(self.root, text="             Select countries            ", command=self.add_country_button_click)
        add_country_button.place(relx=0.72, rely=0.73, anchor=tk.CENTER)
        add_polygon_button = ttk.Button(self.root, text="         Select area manually        ", command=self.add_manual_button_click)
        add_polygon_button.place(relx=0.72, rely=0.77, anchor=tk.CENTER)
        keyboard_coord_button = ttk.Button(self.root, text="             Import area file             ", command=self.keyboard_coords_intro)
        keyboard_coord_button.place(relx=0.72, rely=0.81, anchor=tk.CENTER)
        remove_selection_button = ttk.Button(self.root, text="  Remove selected area (blue)  ",
                                             command=self.erase_selected_countries)
        remove_selection_button.place(relx=0.72, rely=0.85, anchor=tk.CENTER)
        confirm_area_button = ttk.Button(self.root, text="  Confirm selected area (blue)  ", command=self.confirm_area)
        confirm_area_button.place(relx=0.72, rely=0.89, anchor=tk.CENTER)
        restart_selection_button = ttk.Button(self.root, text="        Restart area selection        ", command=self.erase_all_countries)
        restart_selection_button.place(relx=0.72, rely=0.93, anchor=tk.CENTER)
        delete_config_button = ttk.Button(self.root, text="        Delete configuration         ",
                                              command=self.delete_config)
        delete_config_button.place(relx=0.72, rely=0.97, anchor=tk.CENTER)


        # Export section
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.place(relx=0.801, rely=0.9, relwidth=0.2, relheight=0.01)
        export_button = ttk.Button(self.root, text="   Click to export saved configurations   ", command=self.create_excel_file)
        export_button.place(relx=0.9, rely=0.96, anchor=tk.CENTER)
        export_title = tk.Label(self.root, text="EXPORT TRAFFIC MODEL FILE", anchor="w", justify="left")
        export_title.place(relx=0.85, rely=0.91, anchor=tk.NW)

        # Bind the map widget to the click event
        self.map_widget.canvas.bind("<Button-3>", self.map_click)
        self.map_widget.canvas.bind("<Double-Button-3>", self.draw_manual_polygon)

    def set_terminal_distribution(self, terminal_distribution):
        self.terminal_distribution = terminal_distribution

    @staticmethod
    def read_asc(file_path):  # Extract information from asc Population density file
        with open(file_path, 'r') as file:
            # Read heading
            header = []
            for _ in range(6):
                header.append(file.readline().strip())

            # Extract heading information
            ncols = int(header[0].split()[1])
            nrows = int(header[1].split()[1])
            xllcorner = float(header[2].split()[1])
            yllcorner = float(header[3].split()[1])
            cellsize = float(header[4].split()[1])
            nodata_value = float(header[5].split()[1])

            # Read data
            data = np.loadtxt(file)
            # Replace NODATA for NaN for better visualisation
            data[data == nodata_value] = np.nan

        return data, ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value

    def add_country_to_list(self, country):
        self.countries_listbox.insert(tk.END, country)
        self.selected_countries.append(country)

    def add_area_to_list(self):
        self.flag = self.flag + 1
        self.confirmed_area_listbox.insert(tk.END, f"Polygon {self.flag}")

    def saved_config_to_list(self):
        # Add the name to the listbox
        config_name = self.terminal_distribution.config_name
        self.saved_configurations_listbox.insert(tk.END, config_name)

    def add_country_button_click(self):
        self.country_selection_mode = True
        self.manual_polygon_mode = False
        self.instruction_label.config(text="Right click on the map to select a country")

    def add_manual_button_click(self):
        self.manual_polygon_mode = True
        self.manual_polygon_coords = []
        self.country_selection_mode = False
        self.instruction_label.config(text="Right click on the map to add points to the polygon. Double-right-click to finish.")

    def draw_country_polygon(self, country_geom, color):
        polygons = []
        if color == 'blue':
            if isinstance(country_geom, Polygon):
                coords = [(lat, lon) for lon, lat in country_geom.exterior.coords]
                # Save the figure as Polygon Canvas
                self.selected_figures.append(self.map_widget.set_polygon(coords, outline_color="", fill_color=color))
                polygons.append(coords)  # Save coordinates of the figure
            elif hasattr(country_geom, 'geoms'):  # It's a MultiPolygon
                for geom in country_geom.geoms:
                    coords = [(lat, lon) for lon, lat in geom.exterior.coords]
                    self.selected_figures.append(self.map_widget.set_polygon(coords, outline_color="", fill_color=color))
                    polygons.append(coords)
        else:
            if isinstance(country_geom, Polygon):
                coords = [(lat, lon) for lon, lat in country_geom.exterior.coords]
                # Save the figure as Polygon Canvas
                self.confirmed_figures.append(self.map_widget.set_polygon(coords, outline_color="", fill_color=color))
                polygons.append(coords)  # Save coordinates of the figure
            elif hasattr(country_geom, 'geoms'):  # It's a MultiPolygon
                for geom in country_geom.geoms:
                    coords = [(lat, lon) for lon, lat in geom.exterior.coords]
                    self.confirmed_figures.append(self.map_widget.set_polygon(coords, outline_color="", fill_color=color))
                    polygons.append(coords)
        return polygons

    def draw_manual_polygon(self, event):
        if self.manual_polygon_mode and len(self.manual_polygon_coords) > 2:
            self.manual_polygon_coords.append(self.manual_polygon_coords[0])
            self.confirmed_figures.append(self.map_widget.set_polygon(self.manual_polygon_coords, outline_color="", fill_color="green"))
            self.confirmed_polygons.append([self.manual_polygon_coords])
            self.manual_polygon_mode = False
            self.add_area_to_list()
            self.instruction_label.config(text="Polygon successfully drawn")
            self.erase_manual_paths()

    def map_click(self, event):
        if self.country_selection_mode:
            x = event.x
            y = event.y
            coord = self.map_widget.convert_canvas_coords_to_decimal_coords(x, y)
            lat, lon = coord
            point = Point(lon, lat)
            water = 1  # Flag to check if the user clicks on water instead of a country
            for country in self.world.itertuples():
                if country.geometry.contains(point):
                    if country.name not in self.selected_countries:
                        self.add_country_to_list(country.name)
                        polygons = self.draw_country_polygon(country.geometry, color="blue")
                        self.selected_polygons.append(polygons)
                        self.instruction_label.config(text=f"{country.name} selected.")
                    else:
                        self.instruction_label.config(text=f"{country.name} has already been selected.")
                    water = 0
                    break
            if water == 1:
                self.instruction_label.config(text="Select a valid country")
        elif self.manual_polygon_mode:
            coord = self.map_widget.convert_canvas_coords_to_decimal_coords(event.x, event.y)
            lat, lon = coord
            self.manual_polygon_coords.append((lat, lon))
            if len(self.manual_polygon_coords) > 1:
                path = self.map_widget.set_path(self.manual_polygon_coords, color="blue")
                self.manual_paths.append(path)

    def confirm_area(self):
        self.country_selection_mode = False
        self.instruction_label.config(text="Confirmed area selection")

        for country in self.selected_countries:
            for country_data in self.world.itertuples():
                if country_data.name == country:
                    polygon = self.draw_country_polygon(country_data.geometry, color="green")
                    self.confirmed_polygons.append(polygon)
                    break

        # Delete selected countries list
        for country in self.selected_countries:
            self.confirmed_area_listbox.insert(tk.END, country)
        self.countries_listbox.delete(0, tk.END)
        self.selected_countries.clear()
        self.selected_polygons.clear()

    def erase_selected_countries(self):
        for polygon in self.selected_figures:  # Clear selected figures on the map
            polygon.delete()
        self.selected_polygons.clear()
        self.selected_countries.clear()
        self.countries_listbox.delete(0, tk.END)
        self.instruction_label.config(text="New selection erased")
        self.erase_manual_paths()

    def erase_manual_paths(self):
        for path in self.manual_paths:
            path.delete()
        self.manual_paths.clear()

    def erase_all_countries(self):
        self.map_widget.delete_all_polygon()
        self.selected_polygons.clear()  # Clear the list of selected polygons
        self.selected_figures.clear()  # Clear the list of selected figures
        self.confirmed_polygons.clear()  # Clear the list of polygons coordinates
        self.confirmed_figures.clear()  # Clear the list of polygons figures
        self.terminals_coords.clear()  # Clear the list of terminal coordinates
        self.terminals_figures.clear()  # Clear the list of terminal figures
        self.countries_listbox.delete(0, tk.END)
        self.confirmed_area_listbox.delete(0, tk.END)
        self.instruction_label.config(text="Map cleared")
        self.config_index = -1

    def get_random_points(self, quantity, accuracy):
        if not self.confirmed_polygons:
            self.instruction_label.config(text="There are no confirmed selected areas")
            return [], []
        terminals, area = [], []
        # Save the new selected area
        for polygon_coords in self.confirmed_polygons:
            for i in range(len(polygon_coords)):  # Loop in case it is a multipolygon
                area.append(polygon_coords[i])

        start_time = time.time()
        minx, maxx, miny, maxy = float('inf'), float('-inf'), float('inf'), float('-inf')

        # Calculate the limits of the confirmed area
        for polygon in self.confirmed_polygons:
            minx_local, miny_local, maxx_local, maxy_local = self.calculate_polygon_limits(polygon)
            minx = min(minx, minx_local)
            miny = min(miny, miny_local)
            maxx = max(maxx, maxx_local)
            maxy = max(maxy, maxy_local)
        #print(f"Confirmed area boundaries: lats{miny,maxy}, longs{minx,maxx}")

        valid_points = []
        while len(valid_points) < accuracy * quantity:
            created_points = []
            # Creation of random points in rounds of the acuracy * quantity
            longs = np.random.uniform(minx, maxx, accuracy*quantity)
            lats = np.random.uniform(miny, maxy, accuracy*quantity)
            created_points.extend(zip(lats, longs))

            # Check if the points are inside any of the confirmed polygons
            for coords in created_points:
                p = Point(coords)  # Creation of random point
                for polygon_coords in self.confirmed_polygons:
                    for i in range(len(polygon_coords)):  # Loop in case it is a multipolygon
                        polygon = Polygon(polygon_coords[i])  # Create a Shapely Polygon object
                        if polygon.contains(p):
                            valid_points.append(p)
                            break  # Exit the loop if the point is inside a polygon
                    else:
                        continue  # Only executed if the internal loop is not broken
                    break  # Get out of the loop if we found that the point is inside a polygon

        # Selection of the points closer to the population, total number specified in quantity
        # Evaluate all the valid points on the population density function
        densities = np.array([self.get_population_density_at_coordinates(point.x, point.y) for point in valid_points])
        # Sort the points depending on their density value
        sorted_indices = np.argsort(densities)[::-1]
        # Select the desired number of points
        top_indices = sorted_indices[:quantity].tolist()
        terminals = [valid_points[i] for i in top_indices]
        # Add markers
        for terminal in terminals:
            self.add_marker(terminal)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} s")
        return terminals, area

    @staticmethod
    def calculate_polygon_limits(polygon):
        latitudes = []
        longitudes = []
        for ring in polygon:  # Iterate over each ring in the polygon
            for vertex in ring:  # Iterate over each vertex in the ring
                lat, lon = vertex
                latitudes.append(lat)
                longitudes.append(lon)
        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lon, max_lon = min(longitudes), max(longitudes)

        bounds = (min_lon, min_lat, max_lon, max_lat)
        return bounds

    def add_marker(self, point):
        # Get the x and y coordinates from the point
        x, y = point.x, point.y
        self.terminals_coords.append((x,y))
        # Create marker in those coordinates
        marker = self.map_widget.set_polygon([(x, y)], outline_color="blue", fill_color="")
        self.terminals_figures.append(marker)

    def get_population_density_at_coordinates(self, lat, lon):
        # density = self.interpolator((lat,lon))  # Alternative method for density calculation
        density = self.popu_data[int(np.floor(self.f_lat(lat))), int(np.floor(self.f_long(lon)))]
        return density

    def show_saved_configuration(self, event):
        selected_index = self.saved_configurations_listbox.curselection()
        config = self.saved_configs[selected_index[0]]
        self.erase_all_countries()
        if selected_index:
            area_coords = config["Area coords"]
            terminal_coords = config["Terminal coords"]
            for ter_type in terminal_coords: # Redraw the markers
                for terminal in ter_type:
                    marker = self.map_widget.set_polygon([(terminal.x, terminal.y)], outline_color="blue", fill_color="")
                    self.saved_config_markers.append(marker)
            for coords in area_coords:  # Redraw the polygons
                figure = self.map_widget.set_polygon(coords, outline_color="", fill_color="red")
                self.saved_config_figures.append(figure)
                # Add the coordinates to the confirmed polygons to be able to replace over the same area
                self.confirmed_polygons.append([coords])
            self.config_index = selected_index[0]
            self.confirmed_area_listbox.insert(tk.END, f"Geometry {self.saved_configurations_listbox.get(selected_index[0])}")

            self.instruction_label.config(text="")

    def create_excel_file(self):
        # Ask the user for a name for the saved file
        self.excel_name = ""  # Reinitialise excel file's name
        self.excel_name = simpledialog.askstring("Save Traffic_Model", "Introduce name for Excel file:")
        if self.excel_name is None:
            self.instruction_label.config(text="Excel file creation cancelled")
            return
        elif self.excel_name == "":
            self.instruction_label.config(text="Do not enter an empty name, please")
            while self.excel_name == "":
                self.excel_name = simpledialog.askstring("Save Traffic_Model", "Introduce name for Excel file:")

        self.export_file()

    def export_file(self):
        # Create a list of dictionaries with the characteristics of each terminal
        data = [
            {
                'Segment': terminal.segment,
                'ID': terminal.ID,
                'Longitude': terminal.lon,
                'Latitude': terminal.lat,
                'MaxFWD': terminal.maxFWD,
                'MaxRTN': terminal.maxRTN,
                'MinFWD': terminal.minFWD,
                'MinRTN': terminal.minRTN,
                'EIRP': terminal.EIRP,
                'GT': terminal.GT,
            }
            for terminal in self.terminal_distribution.placed_terminals_list
        ]

        # Create a data frame from the dictionary list
        df = pd.DataFrame(data)

        # Export the DataFrame to an excel file
        df.to_excel(f'Core/Excel_Files/{self.excel_name}.xlsx', index=False)

        self.instruction_label.config(text="List exported to Excel successfully")

        for terminal in self.terminal_distribution.placed_terminals_list:
            # Print list of terminals with their characteristics
            terminal.print_terminal_list()
        return

    def keyboard_coords_intro(self):
        lats, longs, name = self.read_coordinates_excel()
        coords = [(lat, lon) for lat, lon in zip(lats, longs)]
        self.confirmed_figures.append(
            self.map_widget.set_polygon(coords, outline_color="", fill_color="green"))
        self.confirmed_polygons.append([coords])
        self.manual_polygon_mode = False
        self.confirmed_area_listbox.insert(tk.END, f"{name}")
        self.instruction_label.config(text="Keyboard coordinates successfully imported")
        self.erase_manual_paths()

    def read_coordinates_excel(self):
        # Choose which file to import
        file_path = self.select_terminal_file()
        df = pd.read_excel(file_path)

        # Lats are in column 4 and longs in 3
        lats = df.iloc[:, 0].dropna().tolist()
        longs = df.iloc[:, 1].dropna().tolist()

        # Export name
        name = os.path.splitext(os.path.basename(file_path))[0]
        return lats, longs, name

    @staticmethod
    def select_terminal_file():
        new_window = tk.Tk()
        new_window.withdraw()  # Hide main window
        script_directory = os.path.dirname(os.path.abspath(__file__))
        initial_directory = os.path.join(script_directory, "Core/Area_coordinates")
        file_path = askopenfilename(title="Select file",
                                    initialdir=initial_directory,
                                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        return file_path

    def delete_config(self):
        if self.config_index == -1:
            self.instruction_label.config(text="Please, select a configuration to erase before")
            return

        number_ter_config = []
        sum_ter_before = 0  # Number of terminals placed on previous saved configurations
        # In order to successfully eliminate the correct terminals we need to know the number of terminals from each configuration
        for index, config in enumerate(self.saved_configs):
            total_ter_config = sum(len(ter_type) for ter_type in config["Terminal coords"])
            number_ter_config.append(total_ter_config)
            if index < self.config_index:
                sum_ter_before = sum(number_ter_config)

        # Delete terminal positions from desired configurations
        del self.terminal_distribution.placed_terminals_list[sum_ter_before:(sum_ter_before + number_ter_config[self.config_index])]

        # Delete configuration dictionary
        del self.saved_configs[self.config_index]

        # Clear listbox
        self.saved_configurations_listbox.delete(self.config_index)
        self.instruction_label.config(text="New selection erased")
        # Clear map
        self.erase_all_countries()


class TerminalDistribution:
    def __init__(self, map_app):
        self.map = map_app
        self.root = map_app.root
        self.terminal_types = []  # If we wanted to introduce predetermined types we could define them here
        self.used_terminal_types = []  # List to store terminal types that we want to place
        self.placed_terminals_list = []  # List to store placed terminals
        self.terminals_per_type_list = []  # List to store the number of terminals per type
        self.terminal_index_list = []  # List to store the types of terminals in case the placed order is different
        self.config_name = ""  # Name for saved configurations
        self.ter_type_index = -1

        # Initialise widgets
        self.separator = ttk.Separator(self.root, orient='vertical')
        self.instruction_label = tk.Label(self.root, text="", anchor="w", justify="left")
        # Create a frame to contain the listbox and scrollbar for the terminal types list
        self.terminal_list_frame = ttk.Frame(self.root)
        self.EIRP_text_box = tk.Text(self.root, height=1, width=32)
        self.GT_text_box = tk.Text(self.root, height=1, width=32)
        self.minFWD_text_box = tk.Text(self.root, height=1, width=32)
        self.maxFWD_text_box = tk.Text(self.root, height=1, width=32)
        self.minRTN_text_box = tk.Text(self.root, height=1, width=32)
        self.maxRTN_text_box = tk.Text(self.root, height=1, width=32)
        self.selection_frame = tk.Frame(self.root, bd=3, relief=tk.SOLID, highlightbackground="black", highlightcolor="white", highlightthickness=0)
        self.instruction_label_repartition = tk.Label(self.root, text="", anchor="w", justify="left")
        self.density_correlation_scale = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL)
        self.total_terminal_number_text_box = tk.Text(self.root, height=1, width=8)
        self.total_terminal_number_text_box.place(relx=0.34, rely=0.104, anchor=tk.NW)

        self.placed_ter_coords = []  # Coordinates for placed terminals each time clicking on apply selection
        self.placed_area_coords = []  # Coordinates for confirmed area each time clicking on apply selection

        self.create_widgets()

    def create_widgets(self):
        self.create_terminal_definition_widgets()
        self.create_terminal_repartition_widgets()
        # SEPARATOR
        self.separator.place(relx=0.2, rely=0, relwidth=0.01, relheight=1)
        #######################################################################################################

    def create_terminal_definition_widgets(self):
        self.terminal_list_frame.place(relx=0.02, rely=0.51, anchor=tk.NW)
        # Create a scrollbar
        scrollbar = ttk.Scrollbar(self.terminal_list_frame, orient=tk.VERTICAL)
        # Create a Listbox to display terminal types
        self.terminal_type_list = tk.Listbox(self.terminal_list_frame, yscrollcommand=scrollbar.set, width=40, height=15)
        # Configure the scrollbar to control the Listbox
        scrollbar.config(command=self.terminal_type_list.yview)
        # Place the Listbox and scrollbar within the frame
        self.terminal_type_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Attach event handler to the ListBox
        self.terminal_type_list.bind("<<ListboxSelect>>", self.show_terminal_type)

        # Create labels for terminal definition
        terminal_definition_title = tk.Label(self.root, text="TERMINAL DEFINITION", anchor="w", justify="left")
        terminal_definition_title.place(relx=0.01, rely=0.01, anchor=tk.NW)
        EIRP_label = tk.Label(self.root, text="EIRP: ", anchor="w", justify="left")
        EIRP_label.place(relx=0.02, rely=0.07, anchor=tk.NW)
        GT_label = tk.Label(self.root, text="G/T: ", anchor="w", justify="left")
        GT_label.place(relx=0.02, rely=0.13, anchor=tk.NW)
        minFWD_label = tk.Label(self.root, text="Min FWD capacity (Mbps): ", anchor="w", justify="left")
        minFWD_label.place(relx=0.02, rely=0.19, anchor=tk.NW)
        maxFWD_label = tk.Label(self.root, text="Max FWD capacity (Mbps): ", anchor="w", justify="left")
        maxFWD_label.place(relx=0.02, rely=0.25, anchor=tk.NW)
        minRTN_label = tk.Label(self.root, text="Min RTN capacity (Mbps): ", anchor="w", justify="left")
        minRTN_label.place(relx=0.02, rely=0.31, anchor=tk.NW)
        maxRTN_label = tk.Label(self.root, text="Max RTN capacity (Mbps): ", anchor="w", justify="left")
        maxRTN_label.place(relx=0.02, rely=0.37, anchor=tk.NW)
        terminal_type_list_title = tk.Label(self.root, text="Terminal Type List: ", anchor="w", justify="left")
        terminal_type_list_title.place(relx=0.02, rely=0.48, anchor=tk.NW)
        self.instruction_label.place(relx=0.02, rely=0.82, anchor=tk.NW)

        # Create textboxes for terminal definition
        self.EIRP_text_box.place(relx=0.02, rely=0.098, anchor=tk.NW)
        self.GT_text_box.place(relx=0.02, rely=0.158, anchor=tk.NW)
        self.minFWD_text_box.place(relx=0.02, rely=0.218, anchor=tk.NW)
        self.maxFWD_text_box.place(relx=0.02, rely=0.278, anchor=tk.NW)
        self.minRTN_text_box.place(relx=0.02, rely=0.338, anchor=tk.NW)
        self.maxRTN_text_box.place(relx=0.02, rely=0.398, anchor=tk.NW)

        # Create buttons for terminal definition
        reset_params_button = ttk.Button(self.root, text="Reset parameters", command=self.reset_parameters)
        reset_params_button.place(relx=0.19, rely=0.43, anchor=tk.NE)
        add_terminal_type_button = ttk.Button(self.root, text="Create new terminal type", command=self.add_terminal_type)
        add_terminal_type_button.place(relx=0.02, rely=0.43, anchor=tk.NW)
        existing_type_button = ttk.Button(self.root, text="  Import terminal definition  ", command=self.import_terminal_type)
        existing_type_button.place(relx=0.1, rely=0.87, anchor=tk.CENTER)
        mod_terminal_type_button = ttk.Button(self.root, text="      Modify terminal type      ", command=self.mod_terminal_type)
        mod_terminal_type_button.place(relx=0.1, rely=0.91, anchor=tk.CENTER)
        delete_terminal_type_button = ttk.Button(self.root, text="    Delete all terminal types   ", command=self.delete_terminal_types)
        delete_terminal_type_button.place(relx=0.1, rely=0.95, anchor=tk.CENTER)

    def create_terminal_repartition_widgets(self):
        # Create frame for terminal placement
        self.selection_frame.place(relx=0.82, rely=0.22, relwidth=0.17, relheight=0.63, anchor=tk.NW)

        # Create labels for terminal repartition
        terminal_repartition_title = tk.Label(self.root, text="TERMINAL REPARTITION", anchor="w", justify="left")
        terminal_repartition_title.place(relx=0.81, rely=0.01, anchor=tk.NW)
        self.instruction_label_repartition.place(relx=0.82, rely=0.145, anchor=tk.NW)
        density_correlation_title = tk.Label(self.root, text="Density correlation: ", anchor="w", justify="left")
        density_correlation_title.place(relx=0.82, rely=0.06, anchor=tk.NW)
        total_terminal_number_button = tk.Label(self.root, text="Total terminal number: ")
        total_terminal_number_button.place(relx=0.82, rely=0.1, anchor=tk.NW)

        # Create scale for density correlation
        self.density_correlation_scale.place(relx=0.915, rely=0.034, anchor=tk.NW)

        # Create textboxes for terminal repartition
        self.total_terminal_number_text_box.place(relx=0.94, rely=0.104, anchor=tk.NW)

        # Create buttons for terminal repartition
        terminal_type_selection_button = ttk.Button(self.root, text="Place selected terminal type", command=self.terminal_type_selection)
        terminal_type_selection_button.place(relx=0.9, rely=0.19, anchor=tk.CENTER)

        del_terminal_repartition_button = ttk.Button(self.root, text="Delete placement", command=self.delete_terminal_placement)
        del_terminal_repartition_button.place(relx=0.81, rely=0.86, anchor=tk.NW)
        apply_terminal_repartition_button = ttk.Button(self.root, text="Apply placement", command=self.apply_placement)
        apply_terminal_repartition_button.place(relx=0.99, rely=0.86, anchor=tk.NE)

    def reset_parameters(self):
        self.instruction_label.config(text="")
        # Clear text boxes
        self.EIRP_text_box.delete("1.0", "end")
        self.GT_text_box.delete("1.0", "end")
        self.minFWD_text_box.delete("1.0", "end")
        self.maxFWD_text_box.delete("1.0", "end")
        self.minRTN_text_box.delete("1.0", "end")
        self.maxRTN_text_box.delete("1.0", "end")
        self.ter_type_index = -1

    def add_terminal_type(self):
        try:
            # Get values from text boxes and convert them to float
            EIRP = float(self.EIRP_text_box.get("1.0", "end-1c").strip())
            GT = float(self.GT_text_box.get("1.0", "end-1c").strip())
            minFWD = float(self.minFWD_text_box.get("1.0", "end-1c").strip())
            maxFWD = float(self.maxFWD_text_box.get("1.0", "end-1c").strip())
            minRTN = float(self.minRTN_text_box.get("1.0", "end-1c").strip())
            maxRTN = float(self.maxRTN_text_box.get("1.0", "end-1c").strip())

            current_type_position = len(self.terminal_types)
            # Create a new terminal dictionary and append to the list
            terminal_type = {
                "Name" : f"Created type {current_type_position}",
                "EIRP": EIRP,
                "G/T": GT,
                "FWD_capacity_min": minFWD,
                "FWD_capacity_max": maxFWD,
                "RTN_capacity_min": minRTN,
                "RTN_capacity_max": maxRTN
            }
            self.terminal_types.append(terminal_type)

            # Update the terminal list label
            self.terminal_type_list.insert(tk.END, f"Terminal type {current_type_position}")

            # Clear text boxes
            self.reset_parameters()
            self.instruction_label.config(text="Terminal type added successfully")
        except ValueError:
            self.instruction_label.config(text="Please enter valid numerical values")

    def import_terminal_type(self):
        # Choose which file to import
        file_path = self.select_terminal_file()
        df = pd.read_excel(file_path)

        # Import of the parameters
        name = df.iloc[:, 0].dropna().tolist()
        EIRP = df.iloc[:, 6].dropna().tolist()
        GT = df.iloc[:, 5].dropna().tolist()
        minFWD = df.iloc[:, 3].dropna().tolist()
        maxFWD = df.iloc[:, 1].dropna().tolist()
        minRTN = df.iloc[:, 4].dropna().tolist()
        maxRTN = df.iloc[:, 2].dropna().tolist()

        for i in range(len(name)):
            # Create a new terminal dictionary and append to the list
            terminal_type = {
                "Name" : name[i],
                "EIRP": EIRP[i],
                "G/T": GT[i],
                "FWD_capacity_min": minFWD[i],
                "FWD_capacity_max": maxFWD[i],
                "RTN_capacity_min": minRTN[i],
                "RTN_capacity_max": maxRTN[i]
            }
            self.terminal_types.append(terminal_type)

            # Update the terminal list label
            self.terminal_type_list.insert(tk.END, name[i])

        # Clear text boxes
        self.reset_parameters()
        if len(name) > 1:
            self.instruction_label.config(text="Terminal types successfully imported")
        else:
            self.instruction_label.config(text="Terminal type successfully imported")

    @staticmethod
    def select_terminal_file():
        new_window = tk.Tk()
        new_window.withdraw()  # Hide main window
        script_directory = os.path.dirname(os.path.abspath(__file__))
        initial_directory = os.path.join(script_directory, "Core/Terminal_types")
        file_path = askopenfilename(title="Select file",
                                    initialdir=initial_directory,
                                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        return file_path

    def show_terminal_type(self, event):
        selected_index = self.terminal_type_list.curselection()
        if selected_index:
            terminal = self.terminal_types[selected_index[0]]
            # Display terminal parameters in the text boxes
            self.EIRP_text_box.delete("1.0", "end")
            self.EIRP_text_box.insert("1.0", terminal["EIRP"])
            self.GT_text_box.delete("1.0", "end")
            self.GT_text_box.insert("1.0", terminal["G/T"])
            self.minFWD_text_box.delete("1.0", "end")
            self.minFWD_text_box.insert("1.0", terminal["FWD_capacity_min"])
            self.maxFWD_text_box.delete("1.0", "end")
            self.maxFWD_text_box.insert("1.0", terminal["FWD_capacity_max"])
            self.minRTN_text_box.delete("1.0", "end")
            self.minRTN_text_box.insert("1.0", terminal["RTN_capacity_min"])
            self.maxRTN_text_box.delete("1.0", "end")
            self.maxRTN_text_box.insert("1.0", terminal["RTN_capacity_max"])
            self.ter_type_index = selected_index[0]

    def mod_terminal_type(self):
        # Check if a terminal type has been created
        if not self.terminal_types:
            self.instruction_label.config(text="No terminal type has been created yet.")
            return

        if self.ter_type_index == -1:
            self.instruction_label.config(text="Please, select terminal type to modify")
            return

        terminal_type = self.terminal_types[self.ter_type_index]

        # Get values from text boxes and convert them to float
        EIRP = float(self.EIRP_text_box.get("1.0", "end-1c").strip())
        GT = float(self.GT_text_box.get("1.0", "end-1c").strip())
        minFWD = float(self.minFWD_text_box.get("1.0", "end-1c").strip())
        maxFWD = float(self.maxFWD_text_box.get("1.0", "end-1c").strip())
        minRTN = float(self.minRTN_text_box.get("1.0", "end-1c").strip())
        maxRTN = float(self.maxRTN_text_box.get("1.0", "end-1c").strip())

        # Change new values
        terminal_type["EIRP"] = EIRP
        terminal_type["G/T"] = GT
        terminal_type["FWD_capacity_min"] = minFWD
        terminal_type["FWD_capacity_max"] = maxFWD
        terminal_type["RTN_capacity_min"] = minRTN
        terminal_type["RTN_capacity_max"] = maxRTN

        self.instruction_label.config(text="Terminal type modified successfully.")
        self.ter_type_index = -1

    def delete_terminal_types(self):
        if not self.terminal_types:
            self.instruction_label.config(text="No terminal type has been created yet.")
            return

        # Deletion of all the types
        self.terminal_types.clear()
        self.used_terminal_types.clear()
        for widget in self.selection_frame.winfo_children():  # Destroy labels on the selection frame
            widget.destroy()
        self.reset_parameters()
        self.terminal_type_list.delete(0, tk.END)
        self.instruction_label.config(text="Terminal types deleted successfully.")

    def terminal_type_selection(self):
        # Check if a terminal type has been created
        if not self.terminal_types:
            self.instruction_label_repartition.config(text="No terminal type has been created yet.")
            return

        # Check if the terminal number is valid
        if self.ter_type_index > -1:
            self.terminal_index_list.append(self.ter_type_index)
            terminal_type = self.terminal_types[self.ter_type_index]

            if terminal_type in self.used_terminal_types:
                self.instruction_label_repartition.config(text="This terminal type has already been selected")
                return

            if len(self.used_terminal_types) >= 12:
                self.instruction_label_repartition.config(text="Maximum terminal types placement reached")
                return

            # Add to the list of used terminal types
            self.used_terminal_types.append(terminal_type)

            # Create labels and textboxes for the placement of the terminal type
            self.placement_labels(self.ter_type_index)

            self.instruction_label_repartition.config(text="Terminal type added to placement")
        else:
            self.instruction_label_repartition.config(text="Select a terminal type")

    def placement_labels(self, index):
        # Create label and textbox for the placement of the selected terminal type
        terminal_type_name = self.terminal_types[index]["Name"]
        terminal_label = tk.Label(self.selection_frame, text=f"{terminal_type_name} Density(%): ", anchor="w", justify="left")
        terminal_label.place(relx=0.02, rely=0.03 + 0.08 * (len(self.used_terminal_types)-1), anchor=tk.NW)
        self.terminal_text_box = tk.Text(self.selection_frame, height=1, width=3)
        self.terminal_text_box.place(relx=0.85, rely=0.03 + 0.08 * (len(self.used_terminal_types)-1), anchor=tk.NW)

    def delete_terminal_placement(self):
        if not self.terminal_types:
            self.instruction_label_repartition.config(text="No terminal type has been created yet.")
            return
        # Deletion of placed terminal types
        self.used_terminal_types.clear()
        for widget in self.selection_frame.winfo_children():  # Destroy labels on the selection frame
            widget.destroy()
        self.reset_parameters()
        self.total_terminal_number_text_box.delete("1.0", "end")
        self.used_terminal_types.clear()  # List to store terminal types that we want to place
        # self.placed_terminals_list.clear()   # List to store placed terminals
        self.terminals_per_type_list.clear()   # List to store the number of terminals per type
        self.terminal_index_list.clear()   # List to store the types of terminals in case the placed order is different
        self.total_terminal_number_text_box.delete("1.0", "end")

        self.instruction_label_repartition.config(text="Terminal types deleted successfully.")

    def apply_placement(self):
        # Clear the list for Terminal Objects and the number of terminals per type
        self.instruction_label_repartition.config(text="Spreading terminals on confirmed areas...")
        self.terminals_per_type_list.clear()
        if not self.map.confirmed_polygons:
            self.instruction_label_repartition.config(text="Please select a region before proceeding")
            return
        # Terminal number calculation
        flag = self.terminal_number_calculation()
        if flag == 0:
            return

        # Ask the user for a name for the saved configuration
        self.config_name = ""  # Reinitialise the name of the saved configuration
        self.config_name = simpledialog.askstring("Save configuration", "Introduce name for saved configuration:")
        if self.config_name is None:
            self.instruction_label_repartition.config(text="Terminal placement cancelled")
            return
        if self.config_name == "":
            self.instruction_label_repartition.config(text="Do not enter an empty name, please")
            while self.config_name == "":
                self.config_name = simpledialog.askstring("Save configuration", "Introduce name for saved configuration:")

        self.map.saved_config_to_list()

        config_ter = []
        # Place terminals
        for index, quantity in enumerate(self.terminals_per_type_list):
            # Terminal placement
            self.random_distribution(index, quantity)
            config_ter.append(self.placed_ter_coords)

        # Printing number of terminal per type
        print(f"Total number of terminals: {sum(self.terminals_per_type_list)}")
        for index, number in enumerate(self.terminals_per_type_list):
            terminal_type_name = self.terminal_types[index]["Name"]
            print(f"Number of {terminal_type_name} terminals: {number}")

        # Save the parameters
        # Create a new configuration dictionary and append it to the list
        config = {
            "Area coords": self.placed_area_coords,
            "Terminal coords": config_ter
        }
        self.map.saved_configs.append(config)
        self.instruction_label_repartition.config(text="Successful terminal placement")

    def terminal_number_calculation(self):
        flag = 0  # Flag to test if the operation was successfull
        if not self.terminal_types:
            self.instruction_label_repartition.config(text="No terminal type has been created yet.")
            return flag

        # Obtain the total number of terminals
        if not self.total_terminal_number_text_box.get("1.0", "end-1c").strip():
            self.instruction_label_repartition.config(text="Please enter total the number of terminals")
            return flag
        total_terminal_number = int(self.total_terminal_number_text_box.get("1.0", "end-1c").strip())

        # Obtain placed terminal types densities
        terminal_densities = []
        sum_densities = 0
        for widget in self.selection_frame.winfo_children():
            if isinstance(widget, tk.Text) and widget != self.total_terminal_number_text_box:
                if not widget.get("1.0", "end-1c").strip():
                    self.instruction_label_repartition.config(text="Please enter densities % for all types")
                    return flag
                density = int(widget.get("1.0", "end-1c").strip())
                terminal_densities.append(density)
                sum_densities += density

        # Verify if all densities for placed terminals have been saved
        if len(terminal_densities) != len(self.used_terminal_types):
            self.instruction_label_repartition.config(text="Please enter densities % for all types")
            return flag
        elif sum_densities != 100:  # Verify that the sum of all percentages is equal to 100%
            self.instruction_label_repartition.config(text="Sum of densities should be equal to 100%")
            return flag

        # Calculate total number of each terminal type
        remaining_terminals = total_terminal_number
        for density in terminal_densities:
            terminals_for_type = int(total_terminal_number * (density / 100.0))  # Converting density to percentage
            self.terminals_per_type_list.append(terminals_for_type)
            remaining_terminals -= terminals_for_type

        # Add the remaining terminals to the first terminal types on the list
        for i in range(remaining_terminals):
            self.terminals_per_type_list[i] += 1

        # Verify if the sum of terminals is equal to the total number of terminals
        if sum(self.terminals_per_type_list) != total_terminal_number:
            self.instruction_label_repartition.config(text="Error: Delete current placement")
            return flag

        # Reset textboxes
        self.total_terminal_number_text_box.delete("1.0", "end")
        for widget in self.selection_frame.winfo_children():
            if isinstance(widget, tk.Text) and widget != self.total_terminal_number_text_box:
                widget.delete("1.0", "end")

        flag = 1
        return flag

    def random_distribution(self, index, quantity):
        # Create points on the selected area
        accuracy = self.density_correlation_scale.get()  # This parameter indicates how many iterations per point we will do
        self.placed_ter_coords, self.placed_area_coords = self.map.get_random_points(quantity, accuracy)

        # Check if the points have been created
        if quantity > 0 and self.placed_ter_coords == []:
            self.instruction_label_repartition.config(text="There has been an error. Please restart terminal placement")
            return

        # Save terminal characteristics with location
        for point in self.placed_ter_coords:
            terminal = self.terminal_types[self.terminal_index_list[index]]
            new_terminal = Terminal(self.config_name, terminal["Name"], point.x, point.y, terminal["EIRP"], terminal["G/T"],
                                    terminal["FWD_capacity_min"], terminal["FWD_capacity_max"], terminal["RTN_capacity_min"], terminal["RTN_capacity_max"])
            self.placed_terminals_list.append(new_terminal)


class Terminal:
    def __init__(self, segment, ID, lat, lon, EIRP, GT, minFWD, maxFWD, minRTN, maxRTN, beam=0, satellite=0):
        self.segment = segment
        self.ID = ID
        self.lat = lat
        self.lon = lon
        self.EIRP = EIRP
        self.GT = GT
        self.minFWD = minFWD
        self.maxFWD = maxFWD
        self.minRTN = minRTN
        self.maxRTN = maxRTN
        self.beam = beam
        self.satellite = satellite

    def print_terminal_list(self):
        print(f"Terminal ID: {self.ID} (lon: {self.lon}, lat: {self.lat}): EIRP: {self.EIRP}, G/T: {self.GT}, "
              f"Min FWD: {self.minFWD}, Max FWD: {self.maxFWD}, Min RTN: {self.minRTN}, Max RTN: {self.maxRTN}")
