This repository contains the files used for the creation of maps for my BSc Geography dissertation exploring whether Greater Manchester’s 2040 Transport Strategy can address transport-related social exclusion (TRSE) alongside its carbon reduction targets.

The "doctors_driving.py", "hospitals_driving.py", "job_centres_driving.py", "primary_driving.py" and "secondary_driving.py" files contain code which produces maps showing the shortest driving time from TRSE-vulnerable Output Areas (OAs) to the nearest key service. These analyses use the A* algorithm (Hart et al., 1968) applied to population-weighted OA centroids.

The "doctors_walking.py", "hospitals_walking.py", "job_centres_walking.py", "primary_walking.py" and "secondary_walking.py" files contain code which produces maps showing the shortest walking time from TRSE-vulnerable OAs to the nearest key service using the same A* approach.

The "doctors_pt.py", "hospitals_pt.py", "job_centres_pt.py", "primary_pt.py" and "secondary_pt.py" files contain code which produces maps showing the shortest public transport travel time using r5py and Greater Manchester GTFS timetable data (Wednesday, 08:00 departure).

Output maps are stored in the "out" folder.

The A* algorithm was used in GEOG30551 Understanding GIS week 9 practical: understaning networks (ran by Jonny Huck) and implemented by me for my dissertation project. Data was sourced from:

Key service locations and networks were sourced from OpenStreetMap. 

TRSE-vulnerable OAs were identified using the Transport for the North dataset:
https://trse.transportforthenorth.com/combined-authority

Population-weighted OA centroids and boundary data were sourced from the Office for National Statistics:
https://geoportal.statistics.gov.uk/datasets/b9b2b2440af240ce9d30a1d39a7507c2_0/explore
https://geoportal.statistics.gov.uk/datasets/f27b6426a93042a1900f5d688fbf9252_0/explore?location=53.343144%2C-2.203893%2C9.02
https://geoportal.statistics.gov.uk/datasets/ons::local-authority-districts-december-2023-boundaries-uk-bgc-2/about
Public transport schedules were sourced from data.gov.uk:
https://www.data.gov.uk/dataset/c3ca6469-7955-4a57-8bfc-58ef2361b797/gm-public-transport-schedules-gtfs
https://geoportal.statistics.gov.uk/datasets/6beafcfd9b9c4c9993a06b6b199d7e6d_0/explore

The Greater Manchester network extract was sourced from Geofabrik:
https://download.geofabrik.de/europe/united-kingdom/england/greater-manchester.html
