# backend/agents/notifier_agent.py
from google.adk.agents import Agent
import os
MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")

notifier_agent = Agent(
    name="notifier_agent",
    model=MODEL,
    instruction="NotifierAgent: format short messages and notifications for ops teams."
)

def format_notification(plan: dict) -> dict:
    # For now return simple dict; can call notifier_agent.run for LLM-crafted messages
    return {"subject": f"Plan for {plan['event_id']}", "body": f"Risk {plan['risk']}, tasks: {plan.get('tasks', [])}"}
