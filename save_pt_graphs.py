# CREATE AVERAGE WALKING SPEED

# set variable for average walking speed
walk_kph = 4.8

# create an average walking speed
metres_per_second = walk_kph * 1000 / 3600

# add travel time (seconds) to each edge
for x, y, z, data in walking_graph.edges(keys = True, data = True):
    data["travel_time"] = data["length"] / metres_per_second

