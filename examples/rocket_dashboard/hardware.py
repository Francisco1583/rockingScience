import math
import random

from .data import BASE_COORDS, INITIAL_TELEMETRY

EARTH_RADIUS_M = 6371000.0


def _haversine_distance_m(lat1, lon1, lat2, lon2):
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


def compute_distance_from_base(telemetry):
    base_lat = BASE_COORDS["latitude"]
    base_lon = BASE_COORDS["longitude"]
    surface_m = _haversine_distance_m(base_lat, base_lon, telemetry["latitude"], telemetry["longitude"])
    altitude = telemetry.get("altitude", 0.0)
    return math.sqrt(surface_m ** 2 + altitude ** 2)


def simulate_telemetry(previous):
    prev = {**INITIAL_TELEMETRY, **(previous or {})}
    altitude = max(0.0, prev["altitude"] + (random.random() - 0.3) * 8)
    velocity = max(0.0, prev["velocity"] + (random.random() - 0.4) * 12)
    acceleration = (random.random() - 0.5) * 18
    latitude = prev["latitude"] + (random.random() - 0.5) * 0.0001
    longitude = prev["longitude"] + (random.random() - 0.5) * 0.0001
    return {
        "altitude": altitude,
        "velocity": velocity,
        "acceleration": acceleration,
        "latitude": latitude,
        "longitude": longitude,
    }


def read_hardware_telemetry():
    """
    Replace this stub with your hardware integration.

    Return a dict with at least:
      - altitude (meters)
      - velocity (km/h or m/s, just be consistent)
      - acceleration (m/s^2)
      - latitude (decimal degrees)
      - longitude (decimal degrees)

    Optionally include distanceFromBase to override the default calculation.
    """
    raise NotImplementedError("Hardware telemetry is not wired yet.")


def normalize_telemetry(raw, previous):
    telemetry = {**INITIAL_TELEMETRY}
    if previous:
        telemetry.update(previous)
    if raw:
        telemetry.update(raw)

    if "distanceFromBase" not in telemetry or telemetry["distanceFromBase"] is None:
        telemetry["distanceFromBase"] = compute_distance_from_base(telemetry)

    return telemetry


def get_telemetry(previous, data_source):
    if data_source == "hardware":
        try:
            raw = read_hardware_telemetry()
        except NotImplementedError:
            raw = simulate_telemetry(previous)
        except Exception:
            raw = previous or {}
    else:
        raw = simulate_telemetry(previous)

    return normalize_telemetry(raw, previous)
