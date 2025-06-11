#!/usr/bin/env python3
"""Test the existing agent using REST API calls."""

import json
import subprocess
import requests
import os

def get_access_token():
    """Get the current access token."""
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"], 
        capture_output=True, text=True
    )
    return result.stdout.strip()

def test_rest_api():
    """Test the agent using REST API."""
    base_url = "https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/5957884075011211264"
    
    # Get access token
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing RisenOne Agent via REST API")
    print("=" * 60)
    
    # First, try to create a session
    print("\n🔥 Step 1: Creating a session")
    session_url = f"{base_url}:createSession"
    session_data = {
        "sessionId": "test-session-123",
        "sessionSpec": {
            "userId": "test_user_rest_api"
        }
    }
    
    try:
        session_response = requests.post(session_url, headers=headers, json=session_data)
        print(f"   Status: {session_response.status_code}")
        print(f"   Response: {session_response.text}")
        
        if session_response.status_code == 200:
            session_info = session_response.json()
            session_name = session_info.get("name", "")
            print(f"   ✅ Session created: {session_name}")
            
            # Now try to query using the session
            print(f"\n🔥 Step 2: Querying via session")
            query_url = f"{base_url}:streamQuery"
            query_data = {
                "session": session_name,
                "input": {
                    "text": "Hello, what can you help me with?"
                }
            }
            
            query_response = requests.post(query_url, headers=headers, json=query_data)
            print(f"   Status: {query_response.status_code}")
            print(f"   Response: {query_response.text}")
            
        else:
            print(f"   ❌ Session creation failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_rest_api() 