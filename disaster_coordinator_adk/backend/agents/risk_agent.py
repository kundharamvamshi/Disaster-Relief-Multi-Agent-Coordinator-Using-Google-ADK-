# backend/agents/risk_agent.py
import os
from google.adk.agents import Agent

MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")

# This agent will accept an 'alert' JSON and return risk_score (0..1)
risk_agent = Agent(
    name="risk_agent",
    model=MODEL,
    instruction=(
        "You are RiskAgent. Given an alert JSON, compute a float risk score between 0 and 1 "
        "and provide a short explanation. Output JSON: {\"risk\": 0.72, \"explain\":\"...\"}"
    ),
)

# helper to call via ADK's run / chat API. Use model.run or similar depending on ADK shape.
def evaluate_risk_via_adk(alert: dict) -> dict:
    """
    Runs the RiskAgent LLM to score the alert.
    If your ADK version exposes agent.run() or agent.chat(), adapt accordingly.
    This is a simple wrapper that sends a prompt + alert as string and expects JSON in response.
    """
    # For many ADK versions you do something like: risk_agent.run(input=...)
    from google.adk import client as adk_client  # optional per-version
    prompt = f"Alert JSON:\n{alert}\n\nReturn JSON: {{\"risk\":<0..1>, \"explain\":\"short\"}}"
    # Fallback approach uses the agent as a plain LLM call:
    try:
        response = risk_agent.run(prompt)
        # attempt parse JSON from response
        import json, re
        text = response.output_text if hasattr(response, "output_text") else str(response)
        # extract first JSON object
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        # fallback: return default heuristic
        return {"risk": 0.5, "explain": "fallback (couldn't parse LLM output)"}
    except Exception:
        # fallback heuristic
        payload = alert.get("payload", {})
        # simple heuristic:
        r = 0.5
        if alert.get("type") == "rainfall":
            r = 0.9 if payload.get("rain_mm", 0) > 150 else 0.7 if payload.get("rain_mm", 0) > 80 else 0.4
        return {"risk": r, "explain": "heuristic fallback"}
