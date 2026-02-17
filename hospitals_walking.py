
# HOSPITAL WALKING NETWORK ANALYSIS

from time import perf_counter

# set start time
start_time = perf_counter()	

# IMPORT DATA

import pandas as pd
from geopandas import read_file
import osmnx as osm
from pickle import load
from pyproj import Geod
from shapely.geometry import LineString
from networkx import NodeNotFound, NetworkXNoPath
from heapq import heappush, heappop

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
def astar_path(G, source, target, heuristic):
    
    # first, make sure that both the `source` and `target` nodes actually exist...
    if source not in G or target not in G:
        raise NodeNotFound(f"Either source ({source}) or target ({target}) is not in the graph")
    
    # create a counter to prevent to ensure that each item in the heap queue will have a unique value (as two could theoretically have the same estimated distance)
    counter = 0

	# initialise a list for the heap queue. This will be a list of tuples, each containing 4 values:
	# `priority`: this is the value on which the list will be sorted by the heap queue algorithm. In 
	# 	 our case, this will be the estimated distance for this node (the network distance from the
	# 	 start to this node + the straight line distance from this node to the end) 
	# `counter`: this is simply a unique number to make sure that the algorithm can sort nodes with 
	# 	 equal `priority` values
	# `node`: the ID of the node to which this entry refers 
	# `cost`: this is the network distance between the start point and the node, used as part of our
	# 	 routing algorithm (storing it prevents us from needing to calculate the same distance multiple 
	# 	 times)
    # `parent`: the ID of the node immediately before this one in the path
    
    queue = [(0, counter, source, 0, None)]

	# dictionary to keep track of the network distance from the start to this node, and the straight
	# 	line distance from this node to the end point. This is used to decide which is the best parent 
	# 	for each node that we record in the `parents`` dictionary
    
    distances = {}

	# dictionary to keep track of the parent of each node that we have explored. This is used when we 
	# 	come to reconstruct the route once we reach the end point
    
    parents = {}
    
    # keep going as long as there are more nodes to search
    while queue:

		# pop the next node, its network distance from the start, and its parent from the queue
        cur_node, cur_net_dist, cur_parent = heappop(queue)[2:]	# use list slicing to ignore the first two items

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
            if distances[cur_node][0] < cur_net_dist:
                continue
         
        ''' Section 3: assessing the node and seeing if it is in the shortest path '''
        
        # add the parent of the current node to the list of parents
        parents[cur_node] = cur_parent

		# get the neighbours for the current node (under assessment)
        for neighbour, edge_data in G[cur_node].items():
            
            # work out the network distance to this neighbour from the start of the path - this
			# 	is simply the distance to the current node (which we already know), plus the
			# 	distance from that node to this neighbour (which is stored in the edge data)
            
            dist_from_start = cur_net_dist + edge_data[0]['length']
      
            # have we already seen this neighbour?
            if neighbour in distances:
    
                # as we have been get the network distance from the start via the previous and straight 
    			#  line distance to the end
                previous_dist_from_start, dist_to_end = distances[neighbour]
    
                # if the previous path we found to this node is shorter, abandon this new path
                if previous_dist_from_start <= dist_from_start:
                    continue
    			
            # if we haven't seen this neighbour before, calculate the straight line distance to the end
            else:
                dist_to_end = heuristic(neighbour, target)
    
            # add the two distances to the distances dictionary
            distances[neighbour] = (dist_from_start, dist_to_end)
    
            # work out the estimated distance for this path (the network distance from the start to 
            #  this node + the straight line distance from this node to the end). This will act as the 
            #  priority value for our heap queue - the route with the shortest estimated didstance will 
            #  be assessed first.
            estimated_dist = dist_from_start + dist_to_end
            
            # increment counter and push to heap
            counter += 1
            heappush(queue, (estimated_dist, counter, neighbour, dist_from_start, cur_node))

    # if the loop finishes, we didn't find a route - raise an exception
    raise NetworkXNoPath(f"Node {target} not reachable from {source}")

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

# open walking graph (use rb not wb as it wwill write over it!!!)
with open('walking_graph.pkl', 'rb') as input:
    walking_graph = load(input)

print(f"graph loaded in: {perf_counter() - start_time} seconds")

