# backend/tools/volunteer_api_tool.py
from typing import Dict

# in a real system, you'd call your volunteer DB or Airtable. We implement a simple allocation simulation.
REGIONAL_CAPACITY = {"Springfield": 120, "Greendale": 80}

def assign_volunteers_tool_func(params: Dict) -> Dict:
    location = params.get("location", "unknown")
    required = int(params.get("required", 10))
    available = REGIONAL_CAPACITY.get(location, 0)
    assigned = min(required, available)
    # reduce pool for demo persistency could be added in a real DB
    return {"status": "ok", "assigned": assigned, "location": location, "required": required}
