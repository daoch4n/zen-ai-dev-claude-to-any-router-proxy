#!/usr/bin/env python3
"""
Test the specific scenario that was causing the OpenRouter error
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_claude_code_scenario():
    """Test the exact scenario that was failing in Claude Code"""
    
    # This simulates the tools that Claude Code might be sending
    tools = [
        {
            "name": "read_file",
            "description": "Read the contents of a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file to read"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "The starting line number to read from"
                    },
                    "end_line": {
                        "type": "integer", 
                        "description": "The ending line number to read to"
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "search_files",
            "description": "Search for patterns in files",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to search in"
                    },
                    "regex": {
                        "type": "string",
                        "description": "Regular expression pattern to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Glob pattern to filter files"
                    }
                },
                "required": ["path", "regex"]
            }
        },
        {
            "name": "list_files",
            "description": "List files and directories",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list recursively"
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_to_file",
            "description": "Write content to a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to write to"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    },
                    "line_count": {
                        "type": "integer",
                        "description": "Number of lines in the file"
                    }
                },
                "required": ["path", "content", "line_count"]
            }
        },
        {
            "name": "execute_command",
            "description": "Execute a CLI command",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The CLI command to execute"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory to execute command in"
                    }
                },
                "required": ["command"]
            }
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": "how do I log an error"
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    print("🔍 Testing Claude Code scenario with multiple tools...")
    print(f"📤 Sending {len(tools)} tools to server")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"📥 Response content types: {[block['type'] for block in result['content']]}")
            if any(block['type'] == 'tool_use' for block in result['content']):
                tool_uses = [block for block in result['content'] if block['type'] == 'tool_use']
                print(f"🔧 Tools used: {[tool['name'] for tool in tool_uses]}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_streaming_scenario():
    """Test the same scenario with streaming enabled"""
    
    tools = [
        {
            "name": "search_files",
            "description": "Search for patterns in files",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to search in"
                    },
                    "regex": {
                        "type": "string",
                        "description": "Regular expression pattern to search for"
                    }
                },
                "required": ["path", "regex"]
            }
        }
    ]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": "how do I log an error"
            }
        ],
        "tools": tools,
        "stream": True
    }
    
    print("\n🔍 Testing streaming scenario...")
    
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
            # Check first few events
            event_count = 0
            for line in response.iter_lines():
                if line and event_count < 15:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('event: '):
                        print(f"🎯 {line_str}")
                        event_count += 1
                    elif line_str.startswith('data: ') and 'tool_use' in line_str:
                        print(f"🔧 Tool use detected in stream")
                        event_count += 1
                elif event_count >= 15:
                    print("... (streaming continues)")
                    break
        else:
            print(f"❌ Streaming failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Specific Error Scenarios")
    print("=" * 50)
    
    test_claude_code_scenario()
    test_streaming_scenario()
    
    print("\n✅ Specific error tests completed!")