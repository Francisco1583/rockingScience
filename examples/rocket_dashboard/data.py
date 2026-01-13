import io

import pandas as pd

BASE_COORDS = {
    "latitude": 19.4567,
    "longitude": -103.5678,
}

DATA_SOURCE = "simulated"
GRAPH_WINDOW = 50
UPDATE_INTERVAL_MS = 200

DATA_CSV = """Day,Temperature,Pressure,Humidity
Monday,22,1012,60
Tuesday,24,1010,55
Wednesday,23,1008,58
Thursday,25,1013,53
Friday,26,1011,50
Saturday,27,1009,48
Sunday,28,1014,46
"""

df_example = pd.read_csv(io.StringIO(DATA_CSV))
DEFAULT_DATASET = df_example.to_dict("list")

INITIAL_TELEMETRY = {
    "altitude": 0.0,
    "velocity": 0.0,
    "latitude": BASE_COORDS["latitude"],
    "longitude": BASE_COORDS["longitude"],
    "distanceFromBase": 0.0,
    "acceleration": 0.0,
}

INITIAL_GRAPH_DATA = {
    "velocity": [0.0] * GRAPH_WINDOW,
    "acceleration": [0.0] * GRAPH_WINDOW,
    "altitude": [0.0] * GRAPH_WINDOW,
}

INITIAL_TIMER = {
    "seconds": 10,
    "ms": 0,
    "mode": "down",
}
