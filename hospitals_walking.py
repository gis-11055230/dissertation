# HOSPITAL WALKING NETWORK ANALYSIS


# IMPORT DATA

from time import perf_counter
import pandas as pd
from geopandas import read_file, GeoDataFrame, points_from_xy
import osmnx as osm
from pickle import load
from pyproj import Geod
from shapely.geometry import LineString
from networkx import NodeNotFound, NetworkXNoPath
from heapq import heappush, heappop
from shapely import STRtree
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.pyplot import subplots, savefig
from numpy import mean


# FUNCTIONS

# ellipsoidal_distance function
def ellipsoidal_distance(node_a, node_b):
    
	"""
	Calculate the 'as the crow flies' distance between two nodes in a graph using
	 the Inverse Vincenty method, via the PyProj library.
	"""
    
	# extract the data (the coordinates) from node_a and node_b
	point_a = walking_graph.nodes(data=True)[node_a]
	point_b = walking_graph.nodes(data=True)[node_b]

	# compute the distance across the WGS84 ellipsoid (the one used by the dataset)
	return Geod(ellps='WGS84').inv(point_a['x'], point_a['y'], point_b['x'], point_b['y'])[2]

# time_heuristic function (to find the fastest route, not just the shortest distance)
def time_heuristic(node_a, node_b, walk_kph = 4.8):
    
    """
    Estimate the time (in seconds) between two nodes using straight line
    distance divided by a conservative maximum speed.
    
    Helps the A* algorithm be more efficient in finding the fastest route
    """
    
    # convert speed from kph (kilometres per hour) to m/s (metres per second)
    walk_mps =(walk_kph * 1000) / 3600
    
    # calculate the distance in metres between node_a and node_b using ellipsoidal_distance function above
    distance_in_metres = ellipsoidal_distance(node_a, node_b)
    
    # return the estimated time (in seconds) between node a and b
    return distance_in_metres / walk_mps

# reconstuct_path function
def reconstruct_path(end_node, parent_node, parents):
    
	"""
	Once we have found the end node of our route, reconstruct the shortest path 
	 to it using the parents list
	"""
    
	# initialise a list that will contain the path, beginning with the current node (the end of the route)
	path = [end_node]
	
	# then get the parent (the node from which we arrived at the end of the route)
	node = parent_node

	# loop back through the list of explored nodes until we reach the start node (the one where parent == None)
	while node is not None:

		# for each node in the path, add it to the path...
		path.append(node)

		# ...and move on to its parent (the one before it in the path)
		node = parents[node]
	
	# finally, reverse the path (so it goes start -> end) and return it
	path.reverse()	# note that this is an 'in place' function that edits the list itself, it does not return anything!
	return path

# path_to_linesting function
def path_to_linestring(start_point, path_list, end_point):
	
    """
	Convert a shortest path to a LineString object
	"""
	
    # initialise the list with the start point
    line = [start_point]
    
    # loop through each node in the shortest path and load into list
    for n in path_list:
        
        # get the relevant node from the graph with lat lng data
        node = walking_graph.nodes(data=True)[n]
        
        # load the lat lng data into the lineString
        line.append([node['x'], node['y']])

	# append end point to list
    line.append(end_point)

	# store as a LineString
    return LineString(line)

# astar_path function
def astar_path(G, source, target, heuristic, weight = "travel_time"):
    
    # first, make sure that both the `source` and `target` nodes actually exist...
    if source not in G or target not in G:
        raise NodeNotFound(f"Either source ({source}) or target ({target}) is not in the graph")
    
    # create a counter to prevent to ensure that each item in the heap queue will have a unique value (as two could theoretically have the same estimated distance)
    counter = 0

	# initialise a list for the heap queue. This will be a list of tuples, each containing 4 values:
	# `priority`: this is the value on which the list will be sorted by the heap queue algorithm. In 
	# our case, this will be the estimated distance for this node (the network distance from the
	# start to this node + the straight line distance from this node to the end) 
	# `counter`: this is simply a unique number to make sure that the algorithm can sort nodes with 
	# equal `priority` values
	# `node`: the ID of the node to which this entry refers 
	# `cost`: this is the network distance between the start point and the node, used as part of our
	# routing algorithm (storing it prevents us from needing to calculate the same distance multiple 
	# times)
    # `parent`: the ID of the node immediately before this one in the path
    
    queue = [(0, counter, source, 0, None)]

	# dictionary to keep track of the network distance from the start to this node, and the straight
	# line distance from this node to the end point. This is used to decide which is the best parent 
	# for each node that we record in the `parents`` dictionary
    
    distances = {}

	# dictionary to keep track of the parent of each node that we have explored. This is used when we 
	# come to reconstruct the route once we reach the end point
    
    parents = {}
    
    # keep going as long as there are more nodes to search
    while queue:

		# pop the next node, its network distance from the start, and its parent from the queue
        cur_node, cur_cost, cur_parent = heappop(queue)[2:]	# use list slicing to ignore the first two items

        ''' Section 1: a series of checks for whether we should reject the node ''' 
    
        # check if we have reached the destination
        if cur_node == target:
    
            # if so, reconstruct the path and return
            return reconstruct_path(cur_node, cur_parent, parents)
    
        ''' Section 2: if we are visiting a node we have already seen '''
    
    	# check if we have already explored this node
        if cur_node in parents:
    
    		# if we are back at the start, abandon this path and try the next one
            if parents[cur_node] is None:
                continue
    
            # if we already have a shorter path to this node, abandon this new path and try the next one
            if distances[cur_node][0] < cur_cost:
                continue
         
        ''' Section 3: assessing the node and seeing if it is in the shortest path '''
        
        # add the parent of the current node to the list of parents
        parents[cur_node] = cur_parent

		# get the neighbours for the current node (under assessment)
        for neighbour, edge_data in G[cur_node].items():
            
            # choose the best parallel edge in the Multigraph based on the weight we care about
            try:
                edge_weight = min(attr[weight] for attr in edge_data.values() if attr.get(weight) is not None)
            
            # if there is no valid weight on any of the parallel edges, then continue
            except ValueError:
                continue
            
            # create a new cost from the start of the network
            new_cost = cur_cost + edge_weight
            
            # have we already seen this neighbour?
            if neighbour in distances:
    
                # as we have been get the network distance from the start via the previous and straight 
    			# line distance to the end
                previous_cost_from_start, cost_to_end = distances[neighbour]
    
                # if the previous path we found to this node is shorter, abandon this new path
                if previous_cost_from_start <= new_cost:
                    continue
    			
            # if we haven't seen this neighbour before, calculate the straight line distance to the end
            else:
                cost_to_end = heuristic(neighbour, target)
    
            # add the two distances to the distances dictionary
            distances[neighbour] = (new_cost, cost_to_end)
    
            # work out the estimated distance for this path (the network distance from the start to 
            # this node + the straight line distance from this node to the end). This will act as the 
            # priority value for our heap queue - the route with the shortest estimated didstance will 
            # be assessed first.
            estimated_cost = new_cost + cost_to_end
            
            # increment counter and push to heap
            counter += 1
            heappush(queue, (estimated_cost, counter, neighbour, new_cost, cur_node))

    # if the loop finishes, we didn't find a route - raise an exception
    raise NetworkXNoPath(f"Node {target} not reachable from {source}")


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


# HOSPITAL LOCATION DATA (USING OSMNX)

# extract hospital locations within the greater manchester buffer polygon
hospitals = osm.features_from_polygon(gm_buffer_geom, tags = {"amenity" : "hospital"})

print(f"there are {len(hospitals)} hospitals in greater manchester (+buffer).")

# create hospital points (sometimes can be polygons points so convesrt it to their centroid if a polygon)
hospital_points = hospitals.geometry.apply(lambda g: g.centroid).to_list()


# GRAPH (WALKING NETWORK)

# set start time
start_time = perf_counter()	

print(f"loading graph...")

# open walking graph (use rb not wb as it will write over it!!!)
with open('walking_graph.pkl', 'rb') as input:
    walking_graph = load(input)

print(f"graph loaded in: {perf_counter() - start_time} seconds")

# CREATE AVERAGE WALKING SPEED

# set variable for average walking speed
walk_kph = 4.8

# create an average walking speed
metres_per_second = walk_kph * 1000 / 3600

# add travel time (seconds) to each edge
for x, y, z, data in walking_graph.edges(keys = True, data = True):
    data["travel_time"] = data["length"] / metres_per_second
    

# SPATIAL INDEX (HOSPITALS)

# create a spatial index for hospitals
hospital_idx = STRtree(hospital_points)


# A* SHORTEST PATH ANALYSIS FOR OA CENTROIDS

# set start time
start_time_astar = perf_counter()	

print(f"starting astar...")

# create an empty list
travel_time_list = []

# for each population point
for id, pop in worst_pop_points.iterrows():
    
    # make a Point of the populations points coord data
    pop_point = pop.geometry
    
    # for each population point, find the nearest node (so that we can do the network analysis)
    from_node = osm.distance.nearest_nodes(walking_graph, pop_point.x, pop_point.y)
    
    # find the nearest hospital to each population point
    try:
        nearest_hospital_id = hospital_idx.nearest([pop_point])[0]
    except TypeError:
        nearest_hospital_id = hospital_idx.nearest(pop_point)
        
    nearest_hospital = hospital_points[nearest_hospital_id]
    
    # find the nearest node to the nearest hospital
    to_node = osm.distance.nearest_nodes(walking_graph, nearest_hospital.x, nearest_hospital.y)
    
    # A* algorithm
    
    # use try statement to catch exceptions
    try:
       	# calculate the shortest path across the network
       	shortest_path = astar_path(walking_graph, from_node, to_node, time_heuristic, weight = "travel_time")
        
        # create a variable to store the total time of the network (in seconds)
        path_time = 0
        
        # loop through the edges in the shortest path
        for edge_start, edge_end in zip(shortest_path[:-1], shortest_path[1:]):
            
            # store edge data
            edge_data = walking_graph.get_edge_data(edge_start, edge_end)
            
            # choose the fastest travel_time parallel edge if multiple edges exist
            path_time += min(attr["travel_time"] for attr in edge_data.values() if attr.get("travel_time") is not None)
    
        # convert seconds to minutes
        path_time_min = path_time / 60
        
        # append the distances list with the length of the network
        travel_time_list.append(path_time_min)
        
    # catch exception for no path available
    except NodeNotFound:
        travel_time_list.append(None)
        continue
 
    # catch exception for no path available
    except NetworkXNoPath:
        travel_time_list.append(None)
        continue
    
# add network to the original dataframe
worst_pop_points["hospital_walking_astar"] = travel_time_list

print(f"network calculated in: {perf_counter() - start_time_astar} seconds")

# check how many routes were successful
valid_times = [t for t in travel_time_list if t is not None]
print(f"Valid routes: {len(valid_times)} / {len(travel_time_list)}")

if len(valid_times) > 0:
    
    # calculate mean
    mean_time = (sum(travel_time_list)) / (len(travel_time_list))

    #report simple statistics
    print(f"Minimum travel time to a hospital from TRSE vulnerable areas: {min(travel_time_list):,.0f} mins.")
    print(f"Mean travel time to a hospital from TRSE vulnerable areas: {mean_time:,.0f} mins.")
    print(f"Maximum travel time to a hospital from TRSE vulnerable areas: {max(travel_time_list):,.0f} mins.")

else:
    print("No valid travel times to summarise.")

# PLOTTING MAP

# create copy of the results with the OA21CD (same in the OA's and worst_pop_points) and the results
results = worst_pop_points[["OA21CD", "hospital_walking_astar"]]

# merge the gm OAs and results so that the OA21CD are corresponding
gm_oas = gm_oas.merge(results, on = "OA21CD", how = "left")

# change crs to be the same
gm_boundary_plot = gm_boundary.to_crs(27700)
gm_oas_plot = gm_oas.to_crs(27700)
hospital_points_plot = GeoDataFrame(geometry = hospital_points, crs = 4326).to_crs(27700)
gm_districts_plot = gm_districts.to_crs(27700)

# create map axis object
fig, my_ax = subplots(1, 1, figsize=(16, 10))

# remove axes
my_ax.axis('off')

# plot the OA's
gm_oas_plot.plot(
    ax = my_ax,						
    column = 'hospital_walking_astar',
    cmap = 'YlOrRd',          
    scheme = 'user_defined',
    classification_kwds = {'bins' :[ 15, 30 ]},
    linewidth = 0.3,			
    edgecolor = 'gray',     
    legend = True,
    missing_kwds = {"color": "#f2f2f2",
                     "label": "Non-TRSE OA"},
    legend_kwds = {
    'loc': 'lower right',
    'title': 'Shortest Walking Time to Nearest Hospital (mins)',
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
labels[-2] = "30+ mins (High Spatial Barrier)"
labels[-3] = "15-30 mins (Moderate Spatial Barrier)"
labels[-4] = "0-15 mins (Low Spatial Barrier)"

for text, new_label in zip(legend.get_texts(), labels):
    text.set_text(new_label)
 
legend.set_title("Walking Time to Nearest Hospital (mins)", prop={'size':10})
for text in legend.get_texts():
    text.set_fontsize(9)

# plot the locations, coloured by distance to hospitals
#hospital_points_plot.plot(
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