#!/usr/bin/env python3
"""
Debug script to see exactly what OpenRouter is rejecting
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_simple_tool_debug():
    """Test with the simplest possible tool to see OpenRouter's error"""
    
    # Very minimal tool
    tools = [
        {
            "name": "simple_tool",
            "description": "A simple tool",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string"
                    }
                },
                "required": ["text"]
            }
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": "Use the simple_tool with text 'hello'"
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    print("🔍 Testing simple tool to debug OpenRouter error...")
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

def test_no_tools_baseline():
    """Test without tools to confirm basic functionality"""
    
    payload = {
        "model": "claude-sonnet-4-20250514", 
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "Hello, just say hi back"
            }
        ],
        "stream": False
    }
    
    print("\n🔍 Testing baseline (no tools)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Baseline works: {result['content'][0]['text']}")
        else:
            print(f"❌ Baseline failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 OpenRouter Debug Testing")
    print("=" * 50)
    
    # Test baseline first
    test_no_tools_baseline()
    
    # Test simple tool
    test_simple_tool_debug()
    
    print("\n✅ Debug tests completed!")