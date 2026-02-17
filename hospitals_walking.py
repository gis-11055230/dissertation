
# HOSPITAL WALKING NETWORK ANALYSIS

from time import perf_counter

# set start time
start_time = perf_counter()	

# IMPORT DATA

import pandas as pd
from geopandas import read_file
import osmnx as osm
from pickle import load

# FUNCTIONS


# LOAD DATA

# TRSE DATA (EXTRACT TOP WORST OAS)

# read the greater manchester trse data from TftN (output areas (OA's))
gm_trse = pd.read_csv("trse_data.csv")

# extract the data of the 10% worst trse areas
worst_10 = gm_trse[gm_trse["eng_trse_10pct"] == True]


# POPULATION POINTS

# read population points from csv file
pop_points = pd.read_csv("pop_points_centroids.csv")

# extract the population points out of the 10% worst gm OA's
worst_pop_points = pop_points[pop_points["OA21CD"].isin(worst_10["name"])]


# GREATER MANCHESTER COMBINED AUTHORITY BOUNDARY

# read all boundaries
combined_authority_boundaries = read_file("CAUTH_MAY_2025_EN_BSC_2688761639956883536/CAUTH_MAY_2025_EN_BSC.shp")

# extract greater manchester's boundaries (in the national grid crs)
gm_boundary = combined_authority_boundaries[combined_authority_boundaries["CAUTH25NM"] == "Greater Manchester"].to_crs(27700)

# create a 10 km buffer around the gm boundary to include neighbouring areas
gm_buffer = gm_boundary.buffer(1000)

# create a geometry object of the buffer to use for OSMnx (change to EPSG: 4326)
gm_buffer_geom = gm_buffer.to_crs(4326).geometry.iloc[0]


# HOSPITAL LOCATION DATA (USING OSMNX)

# extract hospital locations within the greater manchester buffer polygon
hospitals = osm.features_from_polygon(gm_buffer_geom, tags = {"amenity" : "hospital"})

print(f"there are {len(hospitals)} hospitals in greater manchester (+buffer).")


# GRAPH (WALKING NETWORK)

print(f"loading graph...")

with open('driving_graph.pkl', 'rb') as input:
    driving_graph = load(input)


print(f"graph loaded in: {perf_counter() - start_time} seconds")