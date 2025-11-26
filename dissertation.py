# IMPORT DATA

import pandas as pd


# FUNCTIONS


# LOAD DATA

# read the greater manchester trse data from TftN (output areas (OA's))
gm_trse = pd.read_csv("trse_data.csv")


# extract the data of the 10% worst trse areas
worst_10 = gm_trse[gm_trse["eng_trse_10pct"] == True]

print("10% worst TRSE areas:", len(worst_10))


# read population points from csv file
pop_points = pd.read_csv("pop_points_centroids.csv")


# extract the population points out of the 10% worst gm OA's
worst_pop_points = pop_points[pop_points["OA21CD"].isin(worst_10["name"])]

print("Population points in worst 10% areas:", len(worst_pop_points))

