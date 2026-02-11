import math
import pandas as pd

HISTORY_LENGTH = 1200
COUNTDOWN_START_MS = 5000
MAX_TPLUS_MS = 60000
MAX_ALTITUDE_M = 1050.0
XY_RANGE_M = 200.0

INITIAL_TELEMETRY = {
    "time_ms": COUNTDOWN_START_MS,
    "time_tplus": 0,
    "altitude_m": 0.0,
    "velocity_mps": 0.0,
    "acceleration_mps2": 0.0,
    "heading_deg": 90.0,
    "distance_m": 0.0,
    "x_m": 0.0,
    "y_m": 0.0,
    "z_m": 0.0,
    "temperature_c": 22.0,
    "pressure_hpa": 1013.0,
    "status": "COUNTDOWN",
    "phase": "COUNTDOWN",
}

INITIAL_HISTORY = [
    {
        **INITIAL_TELEMETRY,
        "time_s": 0.0,
    }
]

DEFAULT_ANALYTICS_DATA = pd.DataFrame(
    {
        "time_s": [0, 1, 2, 3, 4, 5],
        "altitude_m": [0, 12, 30, 55, 85, 120],
        "velocity_mps": [0, 5, 12, 18, 22, 25],
        "temperature_c": [22.0, 22.4, 22.8, 23.4, 24.1, 24.8],
        "pressure_hpa": [1013, 1012, 1010, 1007, 1004, 1000],
        "heading_deg": [90, 92, 94, 95, 97, 100],
    }
)

DEFAULT_ANALYTICS_STATE = {
    "data_sources": DEFAULT_ANALYTICS_DATA.to_dict("list"),
    "message": None,
    "message_level": None,
    "time_col": "time_s",
    "numeric_cols": ["time_s", "altitude_m", "velocity_mps", "temperature_c", "pressure_hpa", "heading_deg"],
}


def _flight_profile(t_s):
    if t_s <= 20:
        altitude = 1.5 * t_s * t_s
        velocity = 3.0 * t_s
        acceleration = 3.0
        phase = "ASCENT"
    elif t_s <= 35:
        dt = t_s - 20.0
        altitude = 600.0 + 60.0 * dt - 0.5 * 4.0 * dt * dt
        velocity = 60.0 - 4.0 * dt
        acceleration = -4.0
        phase = "APOGEE" if abs(t_s - 35.0) < 0.5 else "COAST"
    elif t_s <= 45:
        dt = t_s - 35.0
        altitude = MAX_ALTITUDE_M + 0.5 * -12.0 * dt * dt
        velocity = -12.0 * dt
        acceleration = -12.0
        phase = "DESCENT"
    elif t_s <= 50:
        dt = t_s - 45.0
        altitude = 450.0 + -120.0 * dt + 0.5 * 22.4 * dt * dt
        velocity = -120.0 + 22.4 * dt
        acceleration = 22.4
        phase = "DESCENT"
    else:
        dt = t_s - 50.0
        altitude = max(0.0, 130.0 - 8.0 * dt)
        velocity = -8.0
        acceleration = 0.0
        phase = "PARACHUTE"

    if t_s >= 60:
        phase = "LANDING"
        velocity = 0.0
        acceleration = 0.0

    return max(0.0, altitude), velocity, acceleration, phase


def _horizontal_motion(t_s):
    heading_deg = (90.0 + 3.0 * t_s) % 360
    heading_rad = math.radians(heading_deg)
    radius = min(XY_RANGE_M * 0.7, 2.0 * t_s)
    x = radius * math.cos(heading_rad)
    y = radius * math.sin(heading_rad)
    distance = math.sqrt(x * x + y * y)
    return x, y, distance, heading_deg


def next_dummy(prev, dt_ms):
    """
    Dummy telemetry generator.

    - Countdown starts at COUNTDOWN_START_MS and decreases to 0.
    - At 0 ms the clock latches T0 and time_tplus starts increasing.
    - After T0 the rocket ascends with a small acceleration profile.
    """
    prev = {**INITIAL_TELEMETRY, **(prev or {})}
    dt_s = dt_ms / 1000.0

    time_ms = max(prev["time_ms"] - dt_ms, 0)
    time_tplus = prev["time_tplus"]

    if time_ms == 0:
        time_tplus = min(time_tplus + dt_ms, MAX_TPLUS_MS)
        t_s = time_tplus / 1000.0
        altitude, velocity, acceleration, phase = _flight_profile(t_s)
        x, y, distance, heading = _horizontal_motion(t_s)
        temperature = prev["temperature_c"] + 0.01 * dt_s
        pressure = max(150.0, prev["pressure_hpa"] - altitude * 0.008)
        status = phase
        if dt_s > 0:
            acceleration = (velocity - prev.get("velocity_mps", 0.0)) / dt_s
    else:
        time_tplus = 0
        altitude = max(0.0, prev["altitude_m"] * 0.98)
        velocity = max(0.0, prev["velocity_mps"] * 0.95)
        distance = max(0.0, prev["distance_m"] * 0.95)
        acceleration = 0.0
        temperature = max(18.0, prev["temperature_c"] - 0.02)
        pressure = min(1018.0, prev["pressure_hpa"] + 0.05)
        status = "COUNTDOWN"
        phase = "COUNTDOWN"
        heading = prev["heading_deg"]
        x = prev["x_m"] * 0.95
        y = prev["y_m"] * 0.95

    return {
        "time_ms": time_ms,
        "time_tplus": time_tplus,
        "altitude_m": altitude,
        "velocity_mps": velocity,
        "acceleration_mps2": acceleration,
        "heading_deg": heading,
        "distance_m": distance,
        "x_m": x,
        "y_m": y,
        "z_m": altitude,
        "temperature_c": temperature,
        "pressure_hpa": pressure,
        "status": status,
        "phase": phase,
    }


def update_history(history, telemetry):
    history = list(history or [])
    time_s = telemetry.get("time_tplus", 0) / 1000.0
    entry = {**telemetry, "time_s": time_s}
    history.append(entry)
    return history[-HISTORY_LENGTH:]
