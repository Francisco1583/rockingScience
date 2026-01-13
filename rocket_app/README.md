Rocket App
==========

Overview
--------
Rocket App is a modular Dash UI with three pages:
- Launch: telemetry cards, countdown, radar, timeline, sparklines.
- Analytics: CSV/Excel upload and Plotly preview, plus Chart Editor.
- Predictive: stub layout for future ML analysis.

This version uses dummy telemetry only. Hardware integration is documented but not implemented.

How to run
----------
1) pip install -r requirements.txt
2) pip install -r examples/requirements.txt
3) pip install -e .
4) python examples/change_datasets.py

Then open http://127.0.0.1:1234

Project structure
-----------------
rocket_app/
    app.py
    routes.py
    components/
        radar.py
        telemetry_cards.py
        countdown.py
        timeline.py
        navigation.py
    pages/
        launch.py
        analytics.py
        predictive.py
    data/
        dummy.py
        interface.py
    callbacks/
        telemetry.py
        radar.py
        analytics.py
    assets/
        rocket.css
    README.md
    requirements.txt

Dummy telemetry
---------------
Data is generated in rocket_app/data/dummy.py.
- next_dummy() simulates a simple ascent profile after T0.
- Countdown starts at 10 seconds and latches to T+ at zero.
- Fields are normalized and stored in telemetry_store.

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
- status: str (COUNTDOWN, T_PLUS, etc)

Units
-----
- altitude_m: meters
- velocity_mps: meters per second
- heading_deg: degrees
- distance_m: meters
- time_ms/time_tplus: milliseconds

Example integration (future)
----------------------------
# rocket_app/data/interface.py
# def read_hardware_telemetry():
#     payload = hardware_client.read()
#     return {
#         "time_ms": payload.countdown_ms,
#         "time_tplus": payload.tplus_ms,
#         "altitude_m": payload.altitude_m,
#         "velocity_mps": payload.velocity_mps,
#         "heading_deg": payload.heading_deg,
#         "distance_m": payload.distance_m,
#         "status": payload.status,
#     }

Then update rocket_app/callbacks/telemetry.py:
# updated = next_dummy(...)  ->  updated = read_hardware_telemetry()

