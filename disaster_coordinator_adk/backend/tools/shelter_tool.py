# backend/tools/shelter_tool.py
import os, requests
from dotenv import load_dotenv
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

def find_nearby_shelters(lat, lon, radius_m=5000, type_filter="school"):
    """
    Use Google Places nearbysearch for shelters. Google Places may classify shelters as 'church',
    'school', 'community_center' etc. You can also maintain your own shelters DB.
    """
    if not GOOGLE_MAPS_API_KEY:
        # fallback: return empty list or local mock
        return [{"name": "Central Shelter", "lat": lat+0.01, "lon": lon+0.01, "capacity": 200}]
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_MAPS_API_KEY,
        "location": f"{lat},{lon}",
        "radius": radius_m,
        "keyword": "shelter OR community center OR school"
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        results = []
        for ritem in data.get("results", [])[:10]:
            loc = ritem["geometry"]["location"]
            results.append({"name": ritem.get("name"), "lat": loc["lat"], "lon": loc["lng"], "place_id": ritem.get("place_id")})
        return results
    except Exception as e:
        print("Places nearby search failed", e)
        return []
