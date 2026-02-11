"""
Hardware interface placeholder.

Implement read_hardware_telemetry() with your device IO when ready.
Do NOT call hardware directly from callbacks.
"""

EXPECTED_FIELDS = {
    "time_ms": "int (ms remaining to T0)",
    "time_tplus": "int (ms since T0)",
    "altitude_m": "float (meters)",
    "velocity_mps": "float (meters per second)",
    "heading_deg": "float (0-360 degrees)",
    "distance_m": "float (meters)",
    "temperature_c": "float (celsius)",
    "pressure_hpa": "float (hPa)",
    "status": "str (COUNTDOWN, T_PLUS, etc)",
}


def read_hardware_telemetry():
    """
    Replace this stub with real hardware integration.

    Return a dict with the fields listed in EXPECTED_FIELDS.
    Keep units consistent with the names (meters, m/s, degrees, ms).
    """
    raise NotImplementedError("Hardware telemetry is not wired yet.")
