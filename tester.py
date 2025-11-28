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

