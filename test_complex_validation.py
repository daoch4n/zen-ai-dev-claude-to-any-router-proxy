#!/usr/bin/env python3
"""
Test complex validation scenarios that might have caused the 422 error
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_complex_tool_conversation():
    """Test a complex conversation that might trigger validation errors"""
    
    # Start with a tool request
    messages = [
        {
            "role": "user",
            "content": "How do I log an error in my code?"
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": messages,
        "tools": [
            {
                "name": "search_patterns",
                "description": "Search for code patterns",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern"
                        },
                        "file_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File types to search"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        ],
        "stream": False
    }
    
    print("🧪 Testing complex tool conversation...")
    
    try:
        # First request
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ First request failed: {response.text}")
            return
            
        result = response.json()
        print(f"✅ First response successful")
        
        # Add Claude's response to conversation
        messages.append({
            "role": "assistant",
            "content": result['content']
        })
        
        # Add tool result (this is where validation might fail)
        if result['stop_reason'] == 'tool_use':
            tool_use = None
            for block in result['content']:
                if block['type'] == 'tool_use':
                    tool_use = block
                    break
            
            if tool_use:
                # Add tool result with complex content
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use['id'],
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Found these error logging patterns:"
                                },
                                {
                                    "type": "text", 
                                    "text": "console.error('Error:', error);\nlogger.error('Failed to process:', error);"
                                }
                            ]
                        }
                    ]
                })
                
                print("🔄 Sending tool result...")
                
                # Second request with tool result
                payload['messages'] = messages
                response2 = requests.post(
                    f"{BASE_URL}/v1/messages",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response2.status_code != 200:
                    print(f"❌ Second request failed: {response2.text}")
                    return
                    
                result2 = response2.json()
                print(f"✅ Second response successful")
                
                # Add follow-up question
                messages.append({
                    "role": "assistant",
                    "content": result2['content']
                })
                
                messages.append({
                    "role": "user",
                    "content": "Can you show me more advanced error handling patterns?"
                })
                
                print("🔄 Sending follow-up question...")
                
                # Third request
                payload['messages'] = messages
                response3 = requests.post(
                    f"{BASE_URL}/v1/messages",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response3.status_code != 200:
                    print(f"❌ Third request failed: {response3.text}")
                    return
                    
                print(f"✅ Third response successful")
                print("🎉 Complex conversation completed successfully!")
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_edge_case_content():
    """Test edge cases that might cause validation errors"""
    
    # Test with mixed content types
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": "Hello"
            },
            {
                "role": "assistant", 
                "content": [
                    {
                        "type": "text",
                        "text": "I'll help you with that."
                    },
                    {
                        "type": "tool_use",
                        "id": "test_tool_123",
                        "name": "test_tool",
                        "input": {"query": "test"}
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "test_tool_123",
                        "content": "Tool executed successfully"
                    }
                ]
            },
            {
                "role": "user",
                "content": "Thanks! What else can you help with?"
            }
        ],
        "stream": False
    }
    
    print("\n🧪 Testing edge case content validation...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Edge case validation successful")
        else:
            print(f"❌ Edge case failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Complex Validation Scenarios")
    print("=" * 50)
    
    test_complex_tool_conversation()
    test_edge_case_content()
    
    print("\n✅ Complex validation tests completed!")