# Import necessary libraries
import numpy as np
from astropy import units as u
from astropy.time import Time
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.twobody.propagation import cowell
from astropy.coordinates import GCRS, ITRS, EarthLocation
from geopy.distance import distance

# Define the six classical orbital elements
a = 7000 * u.km  # Semi-major axis
ecc = 0.001 * u.one  # Eccentricity
inc = 98.7 * u.deg  # Inclination
raan = 0 * u.deg  # Right ascension of the ascending node
argp = 90 * u.deg  # Argument of perigee
nu = 0 * u.deg  # True anomaly

# Define the initial epoch
epoch = Time("2024-01-01 00:00:00", scale="utc")

# Create the orbit
orbit = Orbit.from_classical(Earth, a, ecc, inc, raan, argp, nu, epoch)

# Define the propagation time span (24 hours)
time_span = np.linspace(0, 24 * 3600, num=1000) * u.s

# Propagate the orbit
rr, vv = cowell(orbit, time_span)

# Function to convert ECI coordinates to latitude and longitude
def eci_to_latlon(r, epoch):
    location = EarthLocation.from_geocentric(*r, unit=u.m)
    itrs = ITRS(location, obstime=epoch)
    lat = itrs.geodetic.lat.deg
    lon = itrs.geodetic.lon.deg
    return lat, lon

# Calculate the ground track
ground_track = [eci_to_latlon(r, epoch) for r in rr]

# Define satellite swath width
swath_width = 1000 * u.km  # Example value

# Define the target area (latitude, longitude)
target_lat = 30.0  # Example latitude
target_lon = 45.0  # Example longitude

# Function to check if the satellite covers the target area
def is_within_coverage(lat, lon, target_lat, target_lon, swath_width):
    return distance((lat, lon), (target_lat, target_lon)).km <= swath_width.to(u.km).value / 2

# Calculate the number of revisits
revisit_times = [t for (lat, lon), t in zip(ground_track, time_span) if is_within_coverage(lat, lon, target_lat, target_lon, swath_width)]
num_revisits = len(revisit_times)

# Print the number of revisits
print(f"Number of revisits per day over the target area: {num_revisits}")
