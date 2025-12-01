# backend/agents/planner_agent.py
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from tools.volunteer_api_tool import assign_volunteers_tool_func

MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")
vol_tool = FunctionTool(assign_volunteers_tool_func)

planner_agent = Agent(
    name="planner_agent",
    model=MODEL,
    instruction=(
        "PlannerAgent: Given alert + risk produce a JSON plan with tasks. Use assign_volunteers tool to allocate volunteers."
    ),
    tools=[vol_tool],
)

def plan_via_adk(alert: dict, risk: float):
    """
    Ask planner_agent to produce plan JSON. If ADK method signatures differ, adapt.
    Returns a dict plan.
    """
    try:
        prompt = f"Alert: {alert}\nRisk: {risk}\nProduce JSON plan with tasks and call assign_volunteers tool when needed."
        resp = planner_agent.run(prompt)
        text = resp.output_text if hasattr(resp, "output_text") else str(resp)
        import re, json
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
    except Exception:
        # fallback simple plan
        required = 40 if risk > 0.8 else 12 if risk > 0.5 else 0
        assignment = None
        if required > 0:
            assignment = assign_volunteers_tool_func({"location": alert["location"], "required": required})
        return {"event_id": alert.get("id"), "risk": risk, "tasks": [{"task":"monitor" if required==0 else "assign_volunteers","details":""}], "assignment": assignment}
