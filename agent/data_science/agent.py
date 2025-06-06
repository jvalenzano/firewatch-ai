"""Ultra-minimal agent configuration."""

import os
from datetime import date
from google.genai import types
from google.adk.agents import Agent

# Import the database agent directly (bypasses tools.py complexity)
from .sub_agents.bigquery.agent import database_agent

date_today = date.today()

def return_minimal_instructions():
    return """You are a helpful data assistant. You can query BigQuery databases to answer questions about data."""

# Ultra-minimal root agent - just database queries
root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="ultra_minimal_agent",
    instruction=return_minimal_instructions(),
    global_instruction=f"You help users query data. Today's date: {date_today}",
    sub_agents=[database_agent],  # Use database agent directly
    tools=[],  # No complex tools
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
