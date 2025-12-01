# backend/tools/weather_api_tool.py
import os, requests
from datetime import datetime, timezone,timedelta
import random
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# example: get alerts by searching weather for a list of city names
CITY_TO_COORD = {
  "Hyderabad": {"lat":17.3850, "lon":78.4867},
  "Pune": {"lat":18.5204, "lon":73.8567},
  "Vizag": {"lat":17.6868, "lon":83.2185}
}

def fetch_openweather_alerts_for_city(city):
    coords = CITY_TO_COORD.get(city)
    if not coords or not OPENWEATHER_API_KEY:
        return None
    lat, lon = coords["lat"], coords["lon"]
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,daily&appid={OPENWEATHER_API_KEY}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    # parse as needed — this returns "alerts" if present
    alerts = data.get("alerts", [])
    out = []
    for a in alerts:
        payload = {"description": a.get("description"), "tags": a.get("tags", [])}
        out.append({
            "id": a.get("event", "") + "-" + str(int(datetime.now().timestamp())),
            "type": a.get("event", "weather"),
            "location": city,
            "time": a.get("start", datetime.now(timezone.utc).isoformat()),
            "source": "openweather",
            "confidence": 0.9,
            "payload": payload
        })
    return out

DISASTER_TYPES = [
    "rainfall",
    "flood",
    "cyclone",
    "earthquake",
    "wildfire"
]

LOCATIONS = [
    "Springfield",
    "Hyderabad",
    "Mumbai",
    "Chennai",
    "Delhi",
    "Visakhapatnam",
    "Bengaluru"
]

def poll_alerts_tool_func():
    alerts = []

    # generate 1–4 random alerts
    count = random.randint(1, 4)

    for _ in range(count):
        alert_type = random.choice(DISASTER_TYPES)
        location = random.choice(LOCATIONS)

        alert = {
            "id": f"{alert_type}-{random.randint(100,999)}",
            "type": alert_type,
            "location": location,
            "time": (datetime.utcnow() - timedelta(minutes=random.randint(0,30))).isoformat(),
            "source": "mock-weather-engine",
            "confidence": round(random.uniform(0.6, 0.99), 2),
            "payload": {
                "severity": random.choice(["low", "medium", "high"]),
                "population": random.randint(5000, 200000),
            }
        }

        alerts.append(alert)

    return alerts
