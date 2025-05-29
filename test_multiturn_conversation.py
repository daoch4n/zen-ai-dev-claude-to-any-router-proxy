#!/usr/bin/env python3
"""
Test multi-turn conversation with tool use to verify the "single response" issue is fixed
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_multiturn_tool_conversation():
    """Test a complete multi-turn conversation with tool use"""
    
    # Define a calculator tool
    tools = [
        {
            "name": "calculate",
            "description": "Perform basic arithmetic calculations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number", 
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    ]
    
    print("🧪 Testing Multi-turn Conversation with Tools")
    print("=" * 50)
    
    # Turn 1: User asks for calculation
    messages = [
        {
            "role": "user",
            "content": "Please calculate 15 + 27 for me"
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": messages,
        "tools": tools,
        "stream": False
    }
    
    print("🔄 Turn 1: User asks for calculation")
    print(f"📤 Request: {json.dumps({'messages': messages}, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Turn 1 failed: {response.text}")
            return
            
        result = response.json()
        print(f"📥 Claude's response: {json.dumps(result['content'], indent=2)}")
        
        # Add Claude's response to conversation
        messages.append({
            "role": "assistant",
            "content": result['content']
        })
        
        # Turn 2: Provide tool result
        if result['stop_reason'] == 'tool_use':
            # Find the tool use
            tool_use = None
            for content_block in result['content']:
                if content_block['type'] == 'tool_use':
                    tool_use = content_block
                    break
            
            if tool_use:
                print(f"\n🔧 Tool called: {tool_use['name']} with {tool_use['input']}")
                
                # Simulate tool execution
                if tool_use['name'] == 'calculate':
                    inp = tool_use['input']
                    if inp['operation'] == 'add':
                        result_value = inp['a'] + inp['b']
                    elif inp['operation'] == 'subtract':
                        result_value = inp['a'] - inp['b']
                    elif inp['operation'] == 'multiply':
                        result_value = inp['a'] * inp['b']
                    elif inp['operation'] == 'divide':
                        result_value = inp['a'] / inp['b']
                    
                    tool_result = f"The result is {result_value}"
                else:
                    tool_result = "Tool executed successfully"
                
                # Add tool result to conversation
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use['id'],
                            "content": tool_result
                        }
                    ]
                })
                
                print(f"🔄 Turn 2: Providing tool result: {tool_result}")
                
                # Send conversation with tool result
                payload['messages'] = messages
                
                response2 = requests.post(
                    f"{BASE_URL}/v1/messages",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response2.status_code != 200:
                    print(f"❌ Turn 2 failed: {response2.text}")
                    return
                    
                result2 = response2.json()
                print(f"📥 Claude's final response: {json.dumps(result2['content'], indent=2)}")
                
                # Add Claude's response to conversation
                messages.append({
                    "role": "assistant", 
                    "content": result2['content']
                })
                
                # Turn 3: Ask follow-up question
                messages.append({
                    "role": "user",
                    "content": "Great! Now can you multiply that result by 2?"
                })
                
                print(f"\n🔄 Turn 3: Follow-up question")
                payload['messages'] = messages
                
                response3 = requests.post(
                    f"{BASE_URL}/v1/messages",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response3.status_code != 200:
                    print(f"❌ Turn 3 failed: {response3.text}")
                    return
                    
                result3 = response3.json()
                print(f"📥 Claude's follow-up response: {json.dumps(result3['content'], indent=2)}")
                
                print("\n✅ Multi-turn conversation with tools completed successfully!")
                print("🎉 The 'single response' issue appears to be FIXED!")
                
            else:
                print("❌ No tool use found in response")
        else:
            print("❌ Expected tool use but got different stop reason")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_multiturn_tool_conversation()