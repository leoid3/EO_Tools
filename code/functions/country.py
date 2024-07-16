from config import *
from geopy.geocoders import Nominatim

def get_country_name(coords):
    """
    Permet de trouver le pays en fonction de la latitude et de la longitude.
    """
    try:
        lat = coords[0][0]
        lon = coords[0][1]
        geolocator = Nominatim(user_agent="country")
        location = geolocator.reverse((lat, lon), language='en')
        address = location.raw['address']
        country = address.get('country', '')
        state = address.get('state' '')
        return country, state
    except AttributeError:
        return None

def get_poly_coordinate(country_name, state_name):
    """
    Permet de recuperer les latitudes et longitudes qui composent les frontière d'un pays.
    """
    if 'name' in world.columns:
        country_column = 'name'
    elif 'NAME' in world.columns:
        country_column = 'NAME'
    else:
        raise KeyError("La colonne du nom du pays n'est pas trouvée dans le DataFrame")
    
    final_coords =[]
    poly_coord = []
    country = world[world[country_column] == state_name]
    if not country.empty:
        name = state_name
    else:
        country = world[world[country_column] == country_name]
        name = country_name
    # Vérifie si la géométrie est un MultiPolygon ou un Polygon

    if not country.empty:
        geom = country.geometry.iloc[0]
        if geom.type == 'Polygon':
            country_boundary_coords = geom.exterior.coords[:]
            final_coords.append(country_boundary_coords)
            print(f"\nCoordonnées des frontières de {country_name} (Polygon) :")
            for coord in country_boundary_coords:
                print(coord)
        elif geom.type == 'MultiPolygon':
            print(f"\nCoordonnées des frontières de {country_name} (MultiPolygon) :")
            for polygon in geom.geoms:
                country_boundary_coords = polygon.exterior.coords[:]
                final_coords.append(country_boundary_coords)
                poly_coord.append(final_coords)
                for coord in country_boundary_coords:
                    print(coord)
    else:
        print(f"Les données pour {country_name} n'ont pas été trouvées.")
    return final_coords, name
    