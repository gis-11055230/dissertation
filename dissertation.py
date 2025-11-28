# IMPORT DATA

import pandas as pd
from geopandas import read_file
from shapely.geometry import Point
import geopandas as gpd
from shapely import STRtree


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


# SCHOOL DATA

# read schools in england
schools = pd.read_csv("school_locations.csv", dtype=str, encoding="cp1252" )

# convert the northing and easting columns to numeric (so you can create geometry)
schools["Easting"] = pd.to_numeric(schools["Easting"], errors = "coerce")
schools["Northing"] = pd.to_numeric(schools["Northing"], errors = "coerce")

# create point geometry for schools
schools_gdf = gpd.GeoDataFrame(schools, geometry = gpd.points_from_xy(schools["Easting"], schools["Northing"]), crs = "EPSG:27700" )

# read all boundaries
combined_authority_boundaries = read_file("CAUTH_MAY_2025_EN_BSC_2688761639956883536/CAUTH_MAY_2025_EN_BSC.shp")

# extract greater manchester's boundaries
gm_CA_boundary = combined_authority_boundaries[combined_authority_boundaries["CAUTH25NM"] == "Greater Manchester"]

# create a 10 km buffer to include schools that are not in gm but are close the OA
gm_buffer_geom = gm_CA_boundary.geometry.iloc[0].buffer(10000)

# extract gm schools
gm_schools = schools_gdf[schools_gdf.within(gm_buffer_geom)]

print(len(gm_schools))


