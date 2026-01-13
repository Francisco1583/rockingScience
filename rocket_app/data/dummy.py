import math
import random

import pandas as pd

HISTORY_LENGTH = 60
COUNTDOWN_START_MS = 10000

INITIAL_TELEMETRY = {
    "time_ms": COUNTDOWN_START_MS,
    "time_tplus": 0,
    "altitude_m": 0.0,
    "velocity_mps": 0.0,
    "heading_deg": 90.0,
    "distance_m": 0.0,
    "status": "COUNTDOWN",
}

INITIAL_HISTORY = {
    "altitude_m": [0.0] * HISTORY_LENGTH,
    "velocity_mps": [0.0] * HISTORY_LENGTH,
    "distance_m": [0.0] * HISTORY_LENGTH,
}

DEFAULT_ANALYTICS_DATA = pd.DataFrame(
    {
        "time_s": [0, 1, 2, 3, 4, 5],
        "altitude_m": [0, 12, 30, 55, 85, 120],
        "velocity_mps": [0, 5, 12, 18, 22, 25],
    }
)

DEFAULT_ANALYTICS_STATE = {
    "data_sources": DEFAULT_ANALYTICS_DATA.to_dict("list"),
    "message": None,
    "message_level": None,
}


def _next_heading(prev_heading, dt_s):
    drift = 1.5 * dt_s
    noise = (random.random() - 0.5) * 0.4
    return (prev_heading + drift + noise) % 360


def _dummy_flight_update(prev, dt_s, time_tplus_ms):
    accel = 2.0 + 0.6 * math.sin(time_tplus_ms / 3000)
    accel += (random.random() - 0.5) * 0.3
    velocity = max(0.0, prev["velocity_mps"] + accel * dt_s)
    altitude = max(0.0, prev["altitude_m"] + velocity * dt_s)
    distance = max(0.0, prev["distance_m"] + velocity * dt_s * 0.85)
    return altitude, velocity, distance


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
        time_tplus += dt_ms
        altitude, velocity, distance = _dummy_flight_update(prev, dt_s, time_tplus)
        status = "T_PLUS"
    else:
        time_tplus = 0
        altitude = max(0.0, prev["altitude_m"] * 0.98)
        velocity = max(0.0, prev["velocity_mps"] * 0.95)
        distance = max(0.0, prev["distance_m"] * 0.95)
        status = "COUNTDOWN"

    heading = _next_heading(prev["heading_deg"], dt_s)

    return {
        "time_ms": time_ms,
        "time_tplus": time_tplus,
        "altitude_m": altitude,
        "velocity_mps": velocity,
        "heading_deg": heading,
        "distance_m": distance,
        "status": status,
    }


def update_history(history, telemetry):
    history = history or INITIAL_HISTORY
    updated = {}
    for key, series in history.items():
        value = telemetry.get(key, 0.0)
        new_series = list(series) + [value]
        updated[key] = new_series[-HISTORY_LENGTH:]
    return updated
