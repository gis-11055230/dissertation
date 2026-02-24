# IMPORT DATA

import osmnx as osm
from geopandas import read_file
from osmnx import graph
from pickle import dump, load, HIGHEST_PROTOCOL

# OSMNX SETTINGS

osm.settings.use_cache = True
osm.settings.cache_folder = "./osmnx_cache"
osm.settings.log_console = True
osm.settings.timeout = 180
osm.settings.overpass_settings = "[out:json][timeout:180]"


# GREATER MANCHESTER COMBINED AUTHORITY BOUNDARY

# read all boundaries
combined_authority_boundaries = read_file("CAUTH_MAY_2025_EN_BSC_2688761639956883536/CAUTH_MAY_2025_EN_BSC.shp")

# extract greater manchester's boundaries (in the national grid crs)
gm_boundary = combined_authority_boundaries[combined_authority_boundaries["CAUTH25NM"] == "Greater Manchester"].to_crs(27700)

# create a 1 km buffer around the gm boundary to include neighbouring areas
gm_buffer = gm_boundary.buffer(1000)

# create a geometry object of the buffer to use for OSMnx (change to EPSG: 4326)
gm_buffer_geom = gm_buffer.to_crs(4326).geometry.iloc[0]


# GRAPHS

# create a graph for the walking network of GM and its buffer area using OSMNX
walking_graph = graph.graph_from_polygon(gm_buffer_geom, network_type = "walk", simplify = True, retain_all = False, truncate_by_edge = True)

# save walking network graph
#osm.save_graphml(walking_graph, "walking_graph.graphml")
with open('walking_graph.pkl', 'wb') as output:
    dump(walking_graph, output, HIGHEST_PROTOCOL)

# create a graph for the driving network of GM and its buffer area using OSMNX
driving_graph = graph.graph_from_polygon(gm_buffer_geom, network_type = "drive", simplify = True, retain_all = False, truncate_by_edge = True)

# save driving network graph
#osm.save_graphml(driving_graph, "driving_graph.graphml")
with open('driving_graph.pkl', 'wb') as output:
    dump(driving_graph, output, HIGHEST_PROTOCOL)

# this is how to read it back in
# with open('driving_graph.pkl', 'wb') as input:
#   driving_graph = load(input)

print("Saved graphs!!")