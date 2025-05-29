#!/usr/bin/env python3
"""
Test script to verify tool calling and streaming functionality
"""
import requests
import json
import time

# Test the updated OpenRouter server
BASE_URL = "http://localhost:5001"

def test_tool_calling():
    """Test tool calling functionality"""
    
    # Define a simple tool
    tools = [
        {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    ]
    
    # Test message with tool use
    messages = [
        {
            "role": "user",
            "content": "What's the weather like in San Francisco?"
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": messages,
        "tools": tools,
        "stream": True
    }
    
    print("🧪 Testing tool calling with streaming...")
    print(f"📤 Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("📥 Streaming Response:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_str)
                            print(f"  {json.dumps(data, indent=2)}")
                        except json.JSONDecodeError:
                            print(f"  Raw: {data_str}")
                    elif line_str.startswith('event: '):
                        event = line_str[7:]  # Remove 'event: ' prefix
                        print(f"🎯 Event: {event}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_non_streaming():
    """Test non-streaming functionality"""
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with a simple greeting."
            }
        ],
        "stream": False
    }
    
    print("\n🧪 Testing non-streaming response...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_token_counting():
    """Test token counting endpoint"""
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "messages": [
            {
                "role": "user",
                "content": "Hello! How are you today?"
            }
        ]
    }
    
    print("\n🧪 Testing token counting...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/count_tokens",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Token Count: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Updated OpenRouter Anthropic Server")
    print("=" * 50)
    
    # Test basic functionality first
    test_non_streaming()
    
    # Test token counting
    test_token_counting()
    
    # Test tool calling with streaming
    test_tool_calling()
    
    print("\n✅ Tests completed!")