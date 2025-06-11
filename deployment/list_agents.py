#!/usr/bin/env python3
"""List existing Agent Engine deployments."""

import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

def list_existing_agents():
    """List all existing agent deployments."""
    load_dotenv()
    
    project_id = "risenone-ai-prototype"
    location = "us-central1"
    
    print(f"🔍 Checking for existing agents in project: {project_id}")
    print(f"📍 Location: {location}")
    print("-" * 60)
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    try:
        # List all agent engines
        agents_generator = agent_engines.list()
        agents = list(agents_generator)  # Convert generator to list
        
        if not agents:
            print("❌ No existing agents found in this project/location.")
            return
            
        print(f"✅ Found {len(agents)} existing agent(s):")
        print()
        
        for i, agent in enumerate(agents, 1):
            print(f"🤖 Agent #{i}:")
            print(f"   Resource Name: {agent.resource_name}")
            print(f"   Create Time: {agent.create_time}")
            print(f"   Update Time: {agent.update_time}")
            if hasattr(agent, 'display_name'):
                print(f"   Display Name: {agent.display_name}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        print("This might indicate no agents exist or permission issues.")

if __name__ == "__main__":
    list_existing_agents() 