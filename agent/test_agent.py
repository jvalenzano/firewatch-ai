#!/usr/bin/env python3
"""Quick test script for RisenOne agent"""
import subprocess
import sys

def test_agent():
    print("🧪 Testing RisenOne Agent...")
    
    # Test ADK web launch (background)
    try:
        print("Starting ADK web server...")
        process = subprocess.Popen(['adk', 'web'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Give it time to start
        import time
        time.sleep(3)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ ADK web server started successfully")
            print("🌐 Visit: http://localhost:8000")
            print("💬 Test query: 'Hi, What data do you have access to?'")
            
            # Terminate the process
            process.terminate()
            return True
        else:
            print("❌ ADK web server failed to start")
            stdout, stderr = process.communicate()
            print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        return False

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
