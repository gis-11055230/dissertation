# JOB CENTRES PT NETWORK ANALYSIS


# IMPORT DATA

from time import perf_counter
import pandas as pd
from geopandas import read_file, GeoDataFrame, points_from_xy
import osmnx as osm
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.pyplot import subplots, savefig
from datetime import datetime
import r5py
from pathlib import Path


# LOAD DATA


# TRSE DATA (EXTRACT TOP WORST OAS)

# read the greater manchester trse data from TftN (output areas (OA's))
gm_trse = pd.read_csv("trse_data_new.csv")

# extract the data of the 10% worst trse areas
worst_10 = gm_trse[gm_trse["eng_trse_10pct"] == True]


# POPULATION POINTS

# read population points from csv file
pop_points = pd.read_csv("pop_points_centroids.csv")

# extract the population points out of the 10% worst gm OA's
worst_pop_points = pop_points[pop_points["OA21CD"].isin(worst_10["name"])]

# turn the population points into a geodataframe according to the british national grid
worst_pop_points = GeoDataFrame(worst_pop_points, geometry = points_from_xy(worst_pop_points["x"], worst_pop_points["y"]), crs = 27700)

# convert worst pop points to WGS84
worst_pop_points = (worst_pop_points).to_crs(4326)


# GREATER MANCHESTER COMBINED AUTHORITY BOUNDARY

# read all boundaries
combined_authority_boundaries = read_file("CAUTH_MAY_2025_EN_BSC_2688761639956883536/CAUTH_MAY_2025_EN_BSC.shp")

# extract greater manchester's boundaries (in the national grid crs)
gm_boundary = combined_authority_boundaries[combined_authority_boundaries["CAUTH25NM"] == "Greater Manchester"].to_crs(27700)

# create a 1 km buffer around the gm boundary to include neighbouring areas
gm_buffer = gm_boundary.buffer(1000)

# create a single polygon with the buffer included (so it can be used for OSMnx)
gm_buffer = gm_buffer.union_all()

# create a geometry object of the buffer to use for OSMnx (change to EPSG : 4326)
gm_buffer_geom = GeoDataFrame(geometry = [gm_buffer], crs = 27700).to_crs(4326).geometry.iloc[0]


# DISTRICT BOUNDARIES

# read all the boundaries
districts = read_file("Local_Authority_Districts_December_2023_Boundaries_UK_BGC_-1243688636813977100/LAD_DEC_2023_UK_BGC.shp")

# create a list which contains gm's boroughs
gm_boroughs = ["Bolton","Bury","Manchester","Oldham","Rochdale","Salford","Stockport","Tameside","Trafford","Wigan"]

# extract the gm boroughs from the districts
gm_districts = districts[districts["LAD23NM"].isin(gm_boroughs)]


# OUTPUT AREA BOUNDARIES

# read all OA boundaries
oa_boundaries = read_file("Output_Areas_2021_EW_BGC_V2_-6371128854279904124/OA_2021_EW_BGC_V2.shp").to_crs(27700) 

# store the OA's that are in the GM boundary 
gm_oas = oa_boundaries[oa_boundaries["OA21CD"].isin(gm_trse["name"])]


# JOB CENTRE LOCATION DATA (USING OSMNX)

# extract employment agencies locations within the greater manchester buffer polygon
job_centres = osm.features_from_polygon(gm_buffer_geom, tags = {"office" : "employment_agency"})

print(f"there are {len(job_centres)} job centres in greater manchester (+buffer).")

# create job centres points (sometimes can be polygons points so convesrt it to their centroid if a polygon)
job_centres_points = job_centres.geometry.apply(lambda g: g.centroid).to_list()


# GRAPH (PT NETWORK)

# set start time
start_time = perf_counter()	

print(f"loading graph...")

# load network and the OSM raw data for greater manchester
OSM_PBF = Path("greater-manchester-260304.osm.pbf")
GTFS_ZIP = Path("TfGMgtfsnew.zip")

# create a transport network based on the greater manchester public transport system
transport_network = r5py.TransportNetwork(
    osm_pbf=str(OSM_PBF),
    gtfs=[str(GTFS_ZIP)])

print(f"graph loaded in: {perf_counter() - start_time} seconds")


# PT TRAVEL TIME (FASTEST TO NEAREST JOB CENTRE)

# create origins from worst_pop_points (must be EPSG:4326) to use in the network
origins = worst_pop_points.to_crs(4326)[["OA21CD", "geometry"]].copy()
origins = origins.rename(columns={"OA21CD": "id"})

# create destinations from job_centres_points (must be EPSG:4326) to use in the network
destinations = GeoDataFrame(
    {"id": list(range(len(job_centres_points)))},
    geometry = job_centres_points,
    crs = 4326)

# pick a date to do the network analysis from
departure_time = datetime(2026, 3, 4, 8, 0, 0)  # Wed 08:00

# start a counter
start_time_pt = perf_counter()

print("computing PT travel times...")

# create PT travel times from the population points
travel_matrix = r5py.TravelTimeMatrix(
    transport_network,
    origins = origins,
    destinations = destinations,
    departure = departure_time,
    transport_modes = [r5py.TransportMode.WALK, r5py.TransportMode.TRANSIT])

print(f"PT matrix computed in: {perf_counter() - start_time_pt} seconds")

# get the fastest job centres for each OA centroid
nearest_pt = (
    travel_matrix
    .groupby("from_id", as_index=False)["travel_time"]
    .min()
    .rename(columns={"from_id": "OA21CD", "travel_time": "job_centres_pt_8am"}))

# join back to worst_pop_points
worst_pop_points = worst_pop_points.merge(nearest_pt, on="OA21CD", how="left")

# quick success stats
valid_times = worst_pop_points["job_centres_pt_8am"].dropna().to_list()
print(f"Valid routes: {len(valid_times)} / {len(worst_pop_points)}")

if len(valid_times) > 0:
    print(f"Minimum PT time: {min(valid_times):,.0f} mins.")
    print(f"Mean PT time: {sum(valid_times)/len(valid_times):,.0f} mins.")
    print(f"Maximum PT time: {max(valid_times):,.0f} mins.")
    
else:
    print("No valid PT travel times to summarise.")


# PLOTTING MAP

# create copy of the results with the OA21CD (same in the OA's and worst_pop_points) and the results
results = worst_pop_points[["OA21CD", "job_centres_pt_8am"]]

# merge the gm OAs and results so that the OA21CD are corresponding
gm_oas = gm_oas.merge(results, on = "OA21CD", how = "left")

# change crs to be the same
gm_boundary_plot = gm_boundary.to_crs(27700)
gm_oas_plot = gm_oas.to_crs(27700)
job_centres_points_plot = GeoDataFrame(geometry = job_centres_points, crs = 4326).to_crs(27700)
gm_districts_plot = gm_districts.to_crs(27700)

# create map axis object
fig, my_ax = subplots(1, 1, figsize=(16, 10))

# remove axes
my_ax.axis('off')

# plot the OA's
gm_oas_plot.plot(
    ax = my_ax,						
    column = 'job_centres_pt_8am',
    cmap = 'YlOrRd',          
    scheme = 'user_defined',
    classification_kwds = {'bins' :[ 15, 30, 45]},
    linewidth = 0.15,			
    edgecolor = 'gray',     
    legend = True,
    missing_kwds = {"color": "#f2f2f2",
                     "label": "Non-TRSE OA"},
    legend_kwds = {
    'loc': 'lower right',
    'title': 'Shortest Travel Time to Nearest Job Centre (mins)',
    'frameon': True,
    'borderpad': 0.6,
    'labelspacing': 0.5
    })

# create an outline that exactly matches the OA geometry
gm_outline = gm_oas_plot.geometry.union_all().boundary

# plot the outline
GeoDataFrame(geometry=[gm_outline], crs=gm_oas_plot.crs).plot(
    ax=my_ax,
    color="none",
    edgecolor="black",
    linewidth= 1
    )

# plot the boruoughs boundaries
gm_districts.boundary.plot(
    ax=my_ax,
    color="black",
    linewidth=0.8,
    zorder=5
    )

# modify legend labels manually
legend = my_ax.get_legend()
labels = [text.get_text() for text in legend.get_texts()]

#  replace last label with 10+
labels[-2] = "45+ mins (Very High Spatial Barrier)"
labels[-3] = "30-45 mins (High Spatial Barrier)"
labels[-4] = "15-30 mins (Moderate Spatial Barrier)"
labels[-5] = "0-15 mins (Low Spatial Barrier)"

for text, new_label in zip(legend.get_texts(), labels):
    text.set_text(new_label)
 
legend.set_title("Public Transport Travel Time to Nearest Job Centre (minutes)\n(Departure Date: Wednesday 08:00)", prop={'size':10})
for text in legend.get_texts():
    text.set_fontsize(9)

# plot the locations, coloured by distance to job centres
#job_centres_points_plot.plot(
    #ax = my_ax,
    #linewidth = 0,
    #marker = 'x',
	#markersize = 100,
    #color = 'black',
    #zorder = 4
    #)

# add north arrow
x, y, arrow_length = 0.98, 0.99, 0.1
my_ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
	arrowprops=dict(facecolor='black', width=5, headwidth=15),
	ha='center', va='center', fontsize=20, xycoords=my_ax.transAxes)

# add scalebar
my_ax.add_artist(ScaleBar(dx=1, units="m", location="lower left", length_fraction=0.25))

# save the result
savefig('out/3.png', bbox_inches='tight')
print("done!")