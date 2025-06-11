"""Fire-enhanced data science agent with proper ADK structure."""

import os
from datetime import date
from google.genai import types
from google.adk.agents import Agent

# Import the database agent directly (bypasses tools.py complexity)
from .sub_agents.bigquery.agent import database_agent

date_today = date.today()

def return_fire_instructions():
    return """You are a specialized Fire Risk Analysis Agent. You help users analyze wildfire risk data, weather patterns, and emergency response planning. You can query BigQuery databases containing fire danger ratings (NFDR), weather station data, and fuel moisture information to provide intelligent fire risk assessments."""

# Fire-enhanced root agent with proper ADK structure for REST API
root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="risenone_fire_analysis_agent",
    instruction=return_fire_instructions(),
    global_instruction=f"You are a Fire Risk Analysis Agent specializing in wildfire risk assessment and emergency response decision support. Today's date: {date_today}. You have access to real fire danger data, weather station information, and can perform sophisticated fire risk analysis.",
    description="AI assistant for Forest Service wildfire risk analysis and emergency response decision support. Automates manual fire danger calculations, integrates weather station data, and provides intelligent crew positioning recommendations. Built on ultra-minimal architecture for reliable emergency response operations.",
    sub_agents=[database_agent],  # Use enhanced database agent with fire capabilities
    tools=[],  # Tools are handled by sub-agents
    generate_content_config=types.GenerateContentConfig(
        temperature=0.01,
        max_output_tokens=4096,
        top_p=0.95
    ),
)
