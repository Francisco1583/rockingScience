Rocket App
==========

Overview
--------
Rocket App is a modular Dash UI with three pages:
- Launch: telemetry cards, countdown, radar + 3D, timeline, live charts, CSV download.
- Analytics: CSV/Excel upload, automatic overview plots, plus Chart Editor in a separate tab.
- Predictive: demo "Risk Forecast Report" based on heuristics (not a real forecast).

This version uses dummy telemetry only. Hardware integration is documented but not implemented.

How to run
----------
1) pip install -r requirements.txt
2) pip install -r examples/requirements.txt
3) pip install -e .
4) python change_datasets.py

Then open http://127.0.0.1:1234

CSV format (Analytics/Predictive)
---------------------------------
- First column is time (any name, numeric).
- Remaining numeric columns are auto-plotted in Overview.
- Recommended columns: time_s, altitude_m, velocity_mps, temperature_c, pressure_hpa, heading_deg.

Project structure
-----------------
rocket_app/
    app.py
    routes.py
    components/
        radar.py
        rocket_3d.py
        telemetry_cards.py
        countdown.py
        timeline.py
        upload.py
        navigation.py
    pages/
        launch.py
        analytics.py
        predictive.py
    data/
        dummy.py
        interface.py
        csv_loader.py
    callbacks/
        telemetry.py
        launch_charts.py
        analytics_overview.py
        analytics_editor.py
        radar.py
        rocket_3d.py
        predictive.py
    assets/
        rocket.css
    README.md
    requirements.txt

Dummy telemetry
---------------
Data is generated in rocket_app/data/dummy.py.
- next_dummy() simulates countdown and ascent with T0 latch.
- History is buffered for charts and CSV download.

Hardware integration (future)
-----------------------------
Do NOT implement hardware in callbacks.
Instead, replace the dummy generator with a hardware adapter.

1) Implement read_hardware_telemetry() in rocket_app/data/interface.py.
2) Update rocket_app/callbacks/telemetry.py to call your adapter
   instead of next_dummy().

Expected hardware API
---------------------
Return a dict with these fields:
- time_ms: int (ms remaining to T0)
- time_tplus: int (ms since T0)
- altitude_m: float (meters)
- velocity_mps: float (meters per second)
- heading_deg: float (0-360 degrees)
- distance_m: float (meters)
- temperature_c: float (celsius)
- pressure_hpa: float (hPa)
- status: str (COUNTDOWN, T_PLUS, etc)

Units
-----
- altitude_m: meters
- velocity_mps: meters per second
- heading_deg: degrees
- distance_m: meters
- temperature_c: celsius
- pressure_hpa: hPa
- time_ms/time_tplus: milliseconds

Predictive disclaimer
---------------------
Predictive is a prototype risk scoring based on heuristics/anomaly detection.
It is NOT an official forecast.
