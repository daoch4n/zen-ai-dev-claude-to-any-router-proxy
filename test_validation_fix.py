#!/usr/bin/env python3
"""
Test script to verify the validation fix for malformed tool calls
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_malformed_tool_request():
    """Test with potentially malformed tool content"""
    
    # Simulate a request that might have caused the validation error
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": "How do I log an error in my code?"
            }
        ],
        "tools": [
            {
                "name": "search_code",
                "description": "Search for code patterns",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern"
                        },
                        "file_type": {
                            "type": "string",
                            "description": "File type to search"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        ],
        "stream": False
    }
    
    print("🧪 Testing validation fix for malformed tool calls...")
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

def test_streaming_with_tools():
    """Test streaming with tools to see if validation works"""
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": "Please search for error logging patterns"
            }
        ],
        "tools": [
            {
                "name": "search_patterns",
                "description": "Search for code patterns",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        ],
        "stream": True
    }
    
    print("\n🧪 Testing streaming with validation fix...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Streaming started successfully")
            # Just check first few lines to verify it works
            line_count = 0
            for line in response.iter_lines():
                if line and line_count < 10:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('event: '):
                        print(f"🎯 {line_str}")
                    elif line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            print(f"📥 {json.dumps(data, indent=2)}")
                        except:
                            print(f"📥 {line_str}")
                    line_count += 1
                elif line_count >= 10:
                    print("... (truncated for brevity)")
                    break
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Validation Fixes")
    print("=" * 50)
    
    # Test non-streaming first
    test_malformed_tool_request()
    
    # Test streaming
    test_streaming_with_tools()
    
    print("\n✅ Validation tests completed!")