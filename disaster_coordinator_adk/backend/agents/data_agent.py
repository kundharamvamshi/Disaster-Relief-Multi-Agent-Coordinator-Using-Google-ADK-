# backend/agents/data_agent.py
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from tools.weather_api_tool import poll_alerts_tool_func

MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")

# Create a FunctionTool wrapper so ADK model can call it if needed
weather_tool = FunctionTool(poll_alerts_tool_func)

data_agent = Agent(
    name="data_agent",
    model=MODEL,
    instruction="Data Agent: poll external feeds and normalize alerts.",
    tools=[weather_tool],
)
