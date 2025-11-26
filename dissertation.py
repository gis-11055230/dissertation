# IMPORT DATA
import pandas as pd
import csv

# FUNCTIONS


# LOAD DATA

# read the greater manchester trse data from TftN (output areas (OA's))
gm_trse = pd.read_csv("trse_data.csv")


# extract the data of the 10% worst trse areas
worst_10 = gm_trse[gm_trse["eng_trse_10pct"] == True]

print(len(worst_10))

# SPATIAL INDEX


# PLOTTING MAP

