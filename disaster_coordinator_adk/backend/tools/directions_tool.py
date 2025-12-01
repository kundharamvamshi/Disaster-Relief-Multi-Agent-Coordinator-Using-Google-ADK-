import os
import requests
from dotenv import load_dotenv
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

def estimate_route(origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Return dict: {distance_m, duration_s, polyline}
    If no API key, return None-valued fields as fallback.
    """
    if not GOOGLE_MAPS_API_KEY:
        return {"distance_m": None, "duration_s": None, "polyline": None}
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin_lat},{origin_lon}",
        "destination": f"{dest_lat},{dest_lon}",
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        j = r.json()
        if j.get("routes"):
            route = j["routes"][0]
            leg = route["legs"][0]
            return {
                "distance_m": leg.get("distance", {}).get("value"),
                "duration_s": leg.get("duration", {}).get("value"),
                "polyline": route.get("overview_polyline", {}).get("points")
            }
    except Exception as e:
        # don't crash the server for API issues — return safe fallback and log
        print("Directions API failed:", e)
    return {"distance_m": None, "duration_s": None, "polyline": None}