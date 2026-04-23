This repository contains the files used for the creation of maps for my BSc Geography dissertation
exploring whether Greater Manchester's 2040 Transport Strategy can effectively address issues of
transport-related social exclusion (TRSE) alongside its carbon-reduction targets.

Part of this dissertation uses GIS-based network analysis to conduct a shortest path analysis
from TRSE-vulnerable Output Areas (OAs) to assess vulnerable population's accessibiltiy to
the nearest key service (doctors, hospitals, job centres, primary and secondary schools)

The "doctors_driving.py", "hospitals_driving.py", "job_centres_driving.py", "primary_driving.py" and
"secondary_driving.py" files contain code which produces a map showing the TRSE-vulnerable OAs 
shortest driving time to the nearest queried service. The analysis implemented the A* algorithm,
originally created by Hart et al. (1968), to find the shortest path from TRSE-vulnerable OA weighed-
centroids (origin) to the nearest key service (destination). 

The "doctors_walking.py", "hospitals_walking.py", "job_centres_walking.py", "primary_walking.py" and 
"secondary_walking.py" files contain code which produces a map showing the TRSE-vulnerable OAs 
shortest walking time to the nearest queried service. The analysis implemented the A* algorithm,
originally created by Hart et al. (1968), to find the shortest path from TRSE-vulnerable OA weighed-
centroids (origin) to the nearest key service (destination). 


The "doctors_pt.py", "hospitals_pt.py", "job_centres_pt.py", "primary_pt.py" and "secondary_pt.py"
files contain code which produces a map showing the TRSE-vulnerable OAs shortest public transport time
to the nearest queried service. This code uses r5py (rapid realistic routing with Python). Greater
Manchester's public transit timetable was used and the departure date was wednesday at 8am.

Maps are found in "out" file.

Graphs were created using OSMnx
Key service geolocations were identified using OpenStreetMap (OSM)
TRSE-vulnerable OAs were sourced from Transport for the North's TRSE dataset found here: https://trse.transportforthenorth.com/combined-authority
Population-weighted OA centroid was sourced from Office for National Statistics (ONS) found here: https://geoportal.statistics.gov.uk/datasets/b9b2b2440af240ce9d30a1d39a7507c2_0/explore
Greater Manchester's combined authority boundary was sourced from ONS found here:https://geoportal.statistics.gov.uk/datasets/f27b6426a93042a1900f5d688fbf9252_0/explore?location=53.343144%2C-2.203893%2C9.02
Local authority district boundaries were sourced from ONS found here: https://geoportal.statistics.gov.uk/datasets/ons::local-authority-districts-december-2023-boundaries-uk-bgc-2/about
OA boundaries were sourced from ONS found here:https://geoportal.statistics.gov.uk/datasets/6beafcfd9b9c4c9993a06b6b199d7e6d_0/explore
Greater Manchester's Public Transport Schedule GTFS dataset was sourced from data.gov.uk found here: https://www.data.gov.uk/dataset/c3ca6469-7955-4a57-8bfc-58ef2361b797/gm-public-transport-schedules-gtfs
Greater Manchester's network was sourced from OSM found here: https://download.geofabrik.de/europe/united-kingdom/england/greater-manchester.html
