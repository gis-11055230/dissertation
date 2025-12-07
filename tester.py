import geopandas as gpd
import pandas as pd
    
    
# read schools in england
schools = pd.read_csv("school_locations.csv", dtype=str, encoding="cp1252" )

# convert the northing and easting columns to numeric (so you can create geometry)
schools["Easting"] = pd.to_numeric(schools["Easting"], errors = "coerce")
schools["Northing"] = pd.to_numeric(schools["Northing"], errors = "coerce")

# create point geometry for schools
schools_gdf = gpd.GeoDataFrame(schools, geometry = gpd.points_from_xy(schools["Easting"], schools["Northing"]), crs = "EPSG:27700" )

# extract gm schools
gm_schools = schools_gdf[schools_gdf.within(gm_buffer_geom)]

# IMPORT DATA

import pandas as pd
from geopandas import read_file
import osmnx as osm


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
gm_buffer = gm_boundary.buffer(10000)

# create a geometry object of the buffer to use for OSMnx (change to EPSG: 4326)
gm_buffer_geom = gm_buffer.to_crs(4326).geometry.iloc[0]


# HEALTHCARE LOCATION DATA (USING OSMNX)

# extract hospital locations within the greater manchester buffer polygon
hospitals = osm.features_from_polygon(gm_buffer_geom, tags = {"amenity" : "hospital"})

print(f"there are {len(hospitals)} hospitals in greater manchester (+buffer).")

# extract doctor locations within the greater manchester buffer polygon
doctors = osm.features_from_polygon(gm_buffer_geom, tags = {"amenity" : "doctors"})

print(f"there are {len(doctors)} doctors in greater manchester (+buffer).")


# SCHOOL LOCATION DATA (USING OSMNX)

# extract school locations within the greater manchester buffer polygon (primary and secondary)
schools = osm.features_from_polygon(gm_buffer_geom, tags = {"amenity" : "school"})

print(f"there are {len(schools)} schools in greater manchester (+buffer).")

# extract primary schools from all schools (isced level = 1)
primary_schools = schools[schools["isced:level"] == "1"]

print(f"there are {len(primary_schools)} primary schools in greater manchester (+buffer).")

# extract secondary schools from all schools (isced level = 2 , 3)
secondary_schools = schools[schools["isced:level"].isin(["2" , "3"])]


print(f"there are {len(secondary_schools)} secondary schools in greater manchester (+buffer).")


# JOB CENTRE LOCATION DATA (USING OSMNX)

# extract employment agencies locations within the greater manchester buffer polygon
job_centres = osm.features_from_polygon(gm_buffer_geom, tags = {"office" : "employment_agency"})

print(f"there are {len(job_centres)} job centres in greater manchester (+buffer).")