#!/usr/bin/env python3
"""Simple test of the existing agent with basic questions."""

import vertexai
from vertexai import agent_engines

def simple_test():
    """Test with very basic questions."""
    project_id = "risenone-ai-prototype"
    location = "us-central1"
    agent_resource_id = "projects/481721551004/locations/us-central1/reasoningEngines/5957884075011211264"
    
    print(f"🧪 Simple test of RisenOne Fire Analysis Agent")
    print("=" * 60)
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    try:
        # Get the existing agent
        remote_agent = agent_engines.get(agent_resource_id)
        print(f"✅ Connected to agent")
        
        # Simple test questions
        simple_questions = [
            "Hello, what can you help me with?",
            "What is today's date?",
            "Can you tell me about your capabilities?",
        ]
        
        for i, question in enumerate(simple_questions, 1):
            print(f"\n🔥 Test {i}: {question}")
            
            try:
                # Create session and query
                session = remote_agent.create_session(user_id="simple_test_user")
                session_name = session.get('name') if isinstance(session, dict) else session.resource_name
                
                print(f"   📋 Session: {session_name}")
                
                response_stream = remote_agent.stream_query(
                    session=session_name,
                    input=question
                )
                
                print(f"   🤖 Response: ", end="")
                full_response = ""
                for chunk in response_stream:
                    if hasattr(chunk, 'text') and chunk.text:
                        full_response += chunk.text
                        print(chunk.text, end="", flush=True)
                        
                if not full_response:
                    print("(No response received)")
                else:
                    print()  # New line
                    
                print(f"   ✅ Success")
                
                # Clean up
                remote_agent.delete_session(session=session_name)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    simple_test() 