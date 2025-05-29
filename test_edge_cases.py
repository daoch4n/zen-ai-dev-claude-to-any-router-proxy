#!/usr/bin/env python3
"""
Test edge cases that might trigger OpenRouter errors
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_complex_schema():
    """Test with complex schema that might cause issues"""
    
    tools = [
        {
            "name": "complex_tool",
            "description": "A tool with complex schema",
            "input_schema": {
                "type": "object",
                "properties": {
                    "nested_object": {
                        "type": "object",
                        "properties": {
                            "inner_array": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "value": {"type": "number"}
                                    },
                                    "required": ["id"]
                                }
                            }
                        }
                    },
                    "enum_field": {
                        "type": "string",
                        "enum": ["option1", "option2", "option3"]
                    },
                    "optional_field": {
                        "type": "string",
                        "description": "An optional field"
                    }
                },
                "required": ["nested_object", "enum_field"]
            }
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": "Use the complex_tool with some test data"
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    print("🔍 Testing complex schema...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Complex schema works!")
        else:
            print(f"❌ Complex schema failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_many_tools():
    """Test with many tools (15 tools like in the error)"""
    
    tools = []
    for i in range(15):
        tools.append({
            "name": f"tool_{i}",
            "description": f"Tool number {i}",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": f"Parameter for tool {i}"
                    }
                },
                "required": ["param"]
            }
        })
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": "Choose any tool to use"
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    print("\n🔍 Testing with 15 tools...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Many tools work!")
        else:
            print(f"❌ Many tools failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_problematic_schema_fields():
    """Test with schema fields that might cause issues"""
    
    tools = [
        {
            "name": "problematic_tool",
            "description": "Tool with potentially problematic schema fields",
            "input_schema": {
                "type": "object",
                "properties": {
                    "field_with_default": {
                        "type": "string",
                        "default": "default_value",
                        "description": "Field with default"
                    },
                    "field_with_additional_props": {
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {
                            "known_prop": {"type": "string"}
                        }
                    },
                    "field_with_format": {
                        "type": "string",
                        "format": "email",
                        "description": "Email field"
                    }
                },
                "required": ["field_with_default"]
            }
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": "Use the problematic_tool"
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    print("\n🔍 Testing problematic schema fields...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Problematic fields work!")
        else:
            print(f"❌ Problematic fields failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Edge Cases That Might Cause OpenRouter Errors")
    print("=" * 60)
    
    test_complex_schema()
    test_many_tools()
    test_problematic_schema_fields()
    
    print("\n✅ Edge case tests completed!")