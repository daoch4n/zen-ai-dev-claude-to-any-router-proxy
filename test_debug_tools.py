#!/usr/bin/env python3
"""
Debug script to test tool parameters and see what's causing the error
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_simple_tool():
    """Test with a very simple tool to isolate the issue"""
    
    # Very simple tool definition
    tools = [
        {
            "name": "simple_test",
            "description": "A simple test tool",
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "A simple message"
                    }
                },
                "required": ["message"]
            }
        }
    ]
    
    messages = [
        {
            "role": "user",
            "content": "Please use the simple_test tool with message 'hello'"
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": messages,
        "tools": tools,
        "stream": False  # Test non-streaming first
    }
    
    print("🧪 Testing simple tool (non-streaming)...")
    print(f"📤 Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_no_tools():
    """Test without tools to make sure basic functionality works"""
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "Hello, please respond with a simple greeting."
            }
        ],
        "stream": False
    }
    
    print("\n🧪 Testing without tools...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 Debug Testing OpenRouter Tool Parameters")
    print("=" * 50)
    
    # Test basic functionality first
    test_no_tools()
    
    # Test simple tool
    test_simple_tool()
    
    print("\n✅ Debug tests completed!")