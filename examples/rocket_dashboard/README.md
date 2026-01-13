Rocket Dashboard (Launch + Analytics)
===================================

Overview
--------
This example has two pages:
- /launch: live telemetry tiles, controls, radar, and sparklines.
- /analytics: CSV upload + Dash Chart Editor.

By default the launch page uses dummy telemetry so you can run the UI without hardware.

Run
---
1) pip install -r requirements.txt
2) pip install -r examples/requirements.txt
3) pip install -e .
4) python examples/change_datasets.py

Hardware Integration
--------------------
The telemetry pipeline is isolated in two files:
- examples/rocket_dashboard/hardware.py
- examples/rocket_dashboard/callbacks.py

To connect real hardware:
1) Open examples/rocket_dashboard/data.py and set:
   DATA_SOURCE = "hardware"

2) Implement read_hardware_telemetry() in examples/rocket_dashboard/hardware.py.
   Return a dict with at least these keys:
     altitude        float (meters)
     velocity        float (km/h or m/s)
     acceleration    float (m/s^2)
     latitude        float (decimal degrees)
     longitude       float (decimal degrees)

   Optional:
     distanceFromBase  float (meters). If omitted, it is computed from
                       latitude/longitude and altitude.

Where the data flows
--------------------
- callbacks.update_telemetry() calls get_telemetry() from hardware.py.
- get_telemetry() returns dummy data in "simulated" mode or uses your
  read_hardware_telemetry() implementation when DATA_SOURCE = "hardware".
- The UI updates in update_display() using the stores.

Notes
-----
- If you use serial, UDP, CAN, or another bus, keep the IO in hardware.py
  so the UI stays clean and testable.
- You can swap the simulator logic in simulate_telemetry() to match your
  expected ranges before the hardware is ready.
