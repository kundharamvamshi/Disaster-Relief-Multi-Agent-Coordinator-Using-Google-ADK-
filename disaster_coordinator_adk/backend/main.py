# backend/main.py
"""
Full corrected backend (Option B1 — thread-based alert producer + ADK agents + external tools).
Replace your existing main.py with this file.
"""

import os
import time
import threading
import traceback
import logging
from datetime import datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

# FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local tool imports (ensure these modules exist: tools/*.py)
from tools.weather_api_tool import poll_alerts_tool_func
from tools.geocode_tool import geocode_location
from tools.shelter_tool import find_nearby_shelters
from tools.directions_tool import estimate_route
from tools.volunteer_api_tool import assign_volunteers_tool_func

# Agent helpers (these should be implemented in agents/*.py and return JSON-friendly objects)
# e.g. evaluate_risk_via_adk(alert) -> float, plan_via_adk({"alert":..., "risk":...}) -> dict
from agents.risk_agent import evaluate_risk_via_adk
from agents.planner_agent import plan_via_adk

# Memory
from memory.memory_bank import MemoryBank

# simple lookup for demo: map location names to lat/lon
COORD_MAP = {
    "Springfield": (39.7990, -89.6436),
    "Hyderabad": (17.3850, 78.4867),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Delhi": (28.7041, 77.1025),
    "Bengaluru": (12.9716, 77.5946),
    "Visakhapatnam": (17.6868, 83.2185),
    "Bengaluru Urban": (12.9716, 77.5946)
}


# ADK pieces (we create tool wrappers for visibility but won't rely on any unexpected methods)
try:
    from google.adk.agents import Agent
    from google.adk.tools import FunctionTool
except Exception:
    Agent = None
    FunctionTool = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("disaster-backend")

# App
app = FastAPI(title="Disaster Coordinator Backend (Multi-Agent B1)")

# CORS (allow local dev frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class PollResult(BaseModel):
    id: str
    type: str
    location: str
    time: str
    source: str
    confidence: float
    payload: dict

class PlanResponse(BaseModel):
    event_id: str
    risk: float
    tasks: List[dict]
    assignment: Optional[dict] = None

# Global state
MEMORY = MemoryBank()
alerts_cache = []        # authoritative cache produced by background producer
alerts_lock = threading.Lock()
LOGS_MAX = 1000

# ADK configuration (used only if you want to construct Agents locally)
ADK_MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")
if Agent is not None and FunctionTool is not None:
    try:
        # wrap local tool functions as FunctionTool if available (some ADK versions accept single positional arg)
        try:
            weather_tool = FunctionTool(poll_alerts_tool_func)
        except TypeError:
            # fallback: if FunctionTool expects call signature, wrap in a thin adapter object
            class _FT:
                def __init__(self, func): self._f = func
                def call(self, *a, **k): return self._f()
            weather_tool = _FT(poll_alerts_tool_func)

        try:
            volunteer_tool = FunctionTool(assign_volunteers_tool_func)
        except TypeError:
            class _FT2:
                def __init__(self, func): self._f = func
                def call(self, *a, **k): return self._f(*a, **k)
            volunteer_tool = _FT2(assign_volunteers_tool_func)

        # create a coordinator agent object for observability (we won't rely on specific runtime methods)
        coordinator_agent = Agent(
            name="coordinator_agent",
            model=ADK_MODEL,
            instruction="Coordinator agent for disaster relief. Use tools to poll alerts and assign volunteers.",
            tools=[weather_tool, volunteer_tool],
        )
    except Exception:
        # graceful degradation if ADK is not available at runtime
        coordinator_agent = None
else:
    coordinator_agent = None

# --------------------------
# Helpers
# --------------------------
def now_iso():
    return datetime.now(timezone.utc).isoformat()

def extract_alerts(tool_res):
    """
    Normalize a tool response into a list of alert dicts.
    Accepts:
     - list -> returned as-is
     - dict with keys 'alerts','data','results','items','payload' -> returns the list
     - single alert dict -> wrapped in list
     - otherwise -> empty list
    """
    if isinstance(tool_res, list):
        return tool_res
    if isinstance(tool_res, dict):
        for key in ("alerts", "data", "results", "items", "payload"):
            val = tool_res.get(key)
            if isinstance(val, list):
                return val
        # if the dict looks like a single alert, wrap it
        if any(k in tool_res for k in ("id", "type", "location")):
            return [tool_res]
    return []

def safe_assign_volunteers(params):
    """
    Call volunteer assignment tool safely and return a dict.
    """
    try:
        res = assign_volunteers_tool_func(params)
        # normalize possible shapes
        if isinstance(res, dict):
            return res
        return {"assigned": int(res) if isinstance(res, int) else 0}
    except Exception as e:
        logger.exception("assign_volunteers_tool_func failed")
        return {"assigned": 0, "error": str(e)}

def log_event(evt):
    try:
        MEMORY.log(evt)
    except Exception:
        # fallback: print if memory logging fails
        logger.info("log_event fallback: %s", evt)

# --------------------------
# Background alert producer (thread-based)
# --------------------------
def alert_producer(poll_interval=10):
    """
    Background thread polling poll_alerts_tool_func() to generate alerts.
    Normalizes alerts, assigns coordinates, dedupes, and stores into alerts_cache + MEMORY.
    """
    logger.info("alert_producer started (interval=%s sec)", poll_interval)
    while True:
        try:
            # 1) Poll the weather tool for alerts
            try:
                res = poll_alerts_tool_func()
            except TypeError:
                # some versions require call()
                res = poll_alerts_tool_func()
            new_alerts = extract_alerts(res)

            if not new_alerts:
                time.sleep(poll_interval)
                continue

            added = []

            with alerts_lock:
                existing_ids = {a.get("id") for a in alerts_cache if isinstance(a, dict)}

                for a in new_alerts:
                    if not isinstance(a, dict):
                        continue

                    # ----------------------------
                    # Ensure required fields exist
                    # ----------------------------
                    if not a.get("id"):
                        a["id"] = f"alert-{abs(hash(str(a))) % 10**9}"

                    if not a.get("time"):
                        a["time"] = datetime.now(timezone.utc).isoformat()

                    if not a.get("confidence"):
                        a["confidence"] = float(a.get("confidence", 0.5))

                    # ensure payload exists
                    if "payload" not in a or not isinstance(a["payload"], dict):
                        a["payload"] = {}

                    # ---------------------------------------
                    # Assign coordinates (lat/lon) if missing
                    # ---------------------------------------
                    lat = a["payload"].get("lat")
                    lon = a["payload"].get("lon")

                    # Try geocode first
                    if (not lat or not lon) and callable(geocode_location):
                        try:
                            geo = geocode_location(a.get("location"))
                            if geo:
                                lat, lon = geo
                        except Exception:
                            pass

                    # Fallback coordinate map
                    if (not lat or not lon) and a.get("location"):
                        locname = a["location"]
                        if locname in COORD_MAP:
                            lat, lon = COORD_MAP[locname]

                    # Final assignment
                    if lat and lon:
                        a["payload"]["lat"] = float(lat)
                        a["payload"]["lon"] = float(lon)

                    # ----------------------------
                    # Dedup and store
                    # ----------------------------
                    if a["id"] not in existing_ids:
                        alerts_cache.append(a)
                        existing_ids.add(a["id"])
                        added.append(a)

                        # memory logging
                        try:
                            MEMORY.write_incident(a)
                        except Exception:
                            logger.warning("MEMORY.write_incident failed for %s", a["id"])

            # ----------------------------
            # Logging to console & Memory
            # ----------------------------
            if added:
                logger.info("[alert_producer] added %d alerts", len(added))
                log_event({
                    "type": "alerts_added",
                    "count": len(added),
                    "time": datetime.now(timezone.utc).isoformat()
                })

        except Exception as e:
            logger.error("alert_producer error: %s", e)
            traceback.print_exc()

        # wait before next polling
        time.sleep(poll_interval)



# Start the background thread exactly once
_producer_thread = None
def start_alert_producer_once(poll_interval=10):
    global _producer_thread
    if _producer_thread and _producer_thread.is_alive():
        logger.info("alert_producer thread already running")
        return
    _producer_thread = threading.Thread(target=alert_producer, args=(poll_interval,), daemon=True)
    _producer_thread.start()
    logger.info("Started alert_producer thread (daemon)")

# --------------------------
# FastAPI lifecycle
# --------------------------
@app.on_event("startup")
def on_startup():
    # start producer thread
    poll_interval = int(os.getenv("ALERT_POLL_INTERVAL", "10"))
    start_alert_producer_once(poll_interval)
    logger.info("Backend startup complete")


# --------------------------
# API endpoints
# --------------------------
@app.get("/api/poll_alerts", response_model=List[PollResult])
def api_poll_alerts():
    """
    Return the current alerts cache (list). This returns the authoritative alerts produced by the background thread.
    """
    with alerts_lock:
        # return a shallow copy to avoid mutation races
        copy_list = [a.copy() for a in alerts_cache]
    return copy_list

@app.post("/api/plan/{alert_id}", response_model=PlanResponse)
def api_plan(alert_id: str):
    """
    Create a plan for a given alert id using the Risk and Planner ADK agents.
    This implementation is robust: it always returns a dict with tasks (possibly empty)
    and an assignment (possibly None). It logs actions to MEMORY and logger.
    """
    with alerts_lock:
        alert = next((a for a in alerts_cache if a.get("id") == alert_id), None)

    if not alert:
        logger.warning("api_plan: alert not found: %s", alert_id)
        raise HTTPException(status_code=404, detail="Alert not found")

    logger.info("api_plan: planning for alert %s (%s)", alert_id, alert.get("location"))

    # 1) Risk evaluation (ADK helper or fallback)
    try:
        risk_value = None
        if callable(evaluate_risk_via_adk):
            risk_value = evaluate_risk_via_adk(alert)
        if risk_value is None:
            # fallback heuristic
            conf = float(alert.get("confidence", 0.5))
            if alert.get("type") == "rainfall":
                mm = alert.get("payload", {}).get("rain_mm", 0)
                if mm > 150: risk_value = 0.95
                elif mm > 80: risk_value = 0.8
                else: risk_value = 0.4
            else:
                risk_value = min(1.0, 0.5 * conf)
    except Exception:
        logger.exception("api_plan: risk agent error, using fallback")
        risk_value = 0.5

    # 2) Planner (ADK helper or fallback)
    try:
        plan_result = None
        if callable(plan_via_adk):
            plan_result = plan_via_adk({"alert": alert, "risk": risk_value})
        if not isinstance(plan_result, dict):
            plan_result = {"tasks": []}
    except Exception:
        logger.exception("api_plan: planner agent error, using fallback")
        plan_result = {"tasks": []}

    # Ensure tasks list exists
    tasks = plan_result.get("tasks") if isinstance(plan_result.get("tasks"), list) else []
    assignment = plan_result.get("assignment") if isinstance(plan_result.get("assignment"), dict) else None

    # 3) Assignment: call volunteer tool if high risk or no assignment provided
    try:
        if (assignment is None) and float(risk_value) > 0.5:
            required = 40 if risk_value > 0.8 else 12
            assignment = safe_assign_volunteers({"location": alert.get("location"), "required": required})
            tasks.append({"task": "assign_volunteers", "details": f"Assigned {assignment.get('assigned', 0)} volunteers"})
    except Exception:
        logger.exception("api_plan: assign volunteers failed")

    # 4) Geocode & nearest shelter suggestion (best-effort)
    try:
        lat = alert.get("payload", {}).get("lat")
        lon = alert.get("payload", {}).get("lon")
        if not lat or not lon:
            if callable(geocode_location):
                geo = geocode_location(alert.get("location"))
                if geo:
                    alert["payload"]["lat"], alert["payload"]["lon"] = geo
                    lat, lon = geo

        if lat and lon and callable(find_nearby_shelters):
            shelters = find_nearby_shelters(lat, lon, radius_m=15000)
            if shelters:
                # add top shelter suggestion (best-effort)
                top = shelters[0]
                tasks.append({"task": "recommend_shelter", "details": f"Recommend shelter: {top.get('name')}"})
                if callable(estimate_route):
                    route = estimate_route(lat, lon, top.get("lat"), top.get("lon"))
                    assignment = assignment or {}
                    assignment.update({"recommended_shelter": top, "route": route})
    except Exception:
        logger.exception("api_plan: shelter/routing step failed")

    final_plan = {
        "event_id": alert_id,
        "risk": float(risk_value),
        "tasks": tasks,
        "assignment": assignment
    }

    # persist plan + log
    try:
        MEMORY.write_plan(final_plan)
    except Exception:
        logger.exception("api_plan: MEMORY.write_plan failed")

    log_event({"type": "plan_created", "event_id": alert_id, "risk": float(risk_value), "time": datetime.now(timezone.utc).isoformat()})
    logger.info("api_plan: returning plan for %s with %d tasks", alert_id, len(tasks))
    return final_plan


@app.get("/api/incidents", response_model=List[PollResult])
def api_list_incidents():
    """
    Return incidents recorded in MemoryBank (used earlier in your app).
    """
    try:
        return MEMORY.incidents
    except Exception:
        logger.exception("failed to return MEMORY.incidents")
        return []

@app.get("/api/logs")
def api_logs():
    """
    Return recent logs stored in MemoryBank
    """
    try:
        return {"logs": MEMORY.logs[-200:]}
    except Exception:
        return {"logs": []}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "time": now_iso()}

# End of file
