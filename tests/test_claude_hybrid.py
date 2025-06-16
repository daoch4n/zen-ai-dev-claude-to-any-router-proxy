#!/usr/bin/env python3
"""
Hybrid approach: Use Anthropic-style message formatting with direct HTTP requests
for Azure Databricks. This gives us clean code while maintaining compatibility.
"""

import httpx
import base64
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

class AnthropicStyleDatabricksClient:
    """
    A client that mimics the Anthropic library interface but works with Azure Databricks.
    """
    
    def __init__(self, workspace_instance: str, databricks_token: str):
        self.workspace_instance = workspace_instance
        self.databricks_token = databricks_token
        self.base_url = f"https://{workspace_instance}.azuredatabricks.net/serving-endpoints"
        
        # Create proper Basic auth header
        auth_header = base64.b64encode(f"token:{databricks_token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        
        # HTTP client for reuse
        self.client = httpx.Client(headers=self.headers)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    def create_message(self, 
                      endpoint_name: str,
                      messages: List[Dict[str, str]], 
                      max_tokens: int = 1000,
                      temperature: float = 0.7,
                      model: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a message using Anthropic-style interface but Azure Databricks backend.
        
        Args:
            endpoint_name: Azure Databricks endpoint name (e.g., 'databricks-claude-3-7-sonnet')
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Model name (optional, will be ignored by Databricks)
            
        Returns:
            Response dict in OpenAI/Anthropic compatible format
        """
        url = f"{self.base_url}/{endpoint_name}/invocations"
        
        # Azure Databricks payload format
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add model if specified (though Databricks might ignore it)
        if model:
            payload["model"] = model
            
        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()

class AnthropicStyleMessages:
    """
    Mimics the Anthropic messages interface.
    """
    
    def __init__(self, client: AnthropicStyleDatabricksClient):
        self.client = client
    
    def create(self, 
               endpoint_name: str,
               messages: List[Dict[str, str]], 
               max_tokens: int = 1000,
               temperature: float = 0.7,
               model: Optional[str] = None) -> Dict[str, Any]:
        """Create a message - mimics anthropic.messages.create() interface."""
        return self.client.create_message(
            endpoint_name=endpoint_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )

def test_hybrid_approach():
    """Test the hybrid approach."""
    
    # Configuration from environment variables
    workspace_instance = os.getenv("DATABRICKS_HOST")
    databricks_token = os.getenv("DATABRICKS_TOKEN")
    
    # Check if required environment variables are set
    if not workspace_instance or not databricks_token:
        print("❌ Error: DATABRICKS_HOST and DATABRICKS_TOKEN environment variables are required!")
        print("Please set them in your .env file or export them:")
        print("export DATABRICKS_HOST='your-workspace-host.azuredatabricks.net'")
        print("export DATABRICKS_TOKEN='your-databricks-token'")
        print("\nSee .env.example for the expected format.")
        return
    
    print("🚀 Testing Hybrid Anthropic-Style Azure Databricks Client\n")
    
    with AnthropicStyleDatabricksClient(workspace_instance, databricks_token) as client:
        messages_api = AnthropicStyleMessages(client)
        
        # Test endpoints
        endpoints = [
            "databricks-claude-3-7-sonnet",
            "databricks-claude-sonnet-4"
        ]
        
        test_messages = [
            {"role": "user", "content": "Hello! What's your name?"},
        ]
        
        for endpoint in endpoints:
            print(f"📋 Testing {endpoint}")
            print("="*50)
            
            try:
                # This looks just like the Anthropic library!
                response = messages_api.create(
                    endpoint_name=endpoint,
                    messages=test_messages,
                    max_tokens=150,
                    temperature=0.7,
                    model="claude-3-5-sonnet-20241022"  # Optional, might be ignored
                )
                
                print("✅ SUCCESS!")
                
                # Extract response content (handles both formats)
                if 'choices' in response and len(response['choices']) > 0:
                    content = response['choices'][0]['message']['content']
                elif 'content' in response:
                    content = response['content']
                else:
                    content = str(response)
                
                print(f"Response: {content[:200]}...")
                
                # Show usage info if available
                if 'usage' in response:
                    usage = response['usage']
                    print(f"Usage: {usage['prompt_tokens']} prompt + {usage['completion_tokens']} completion = {usage['total_tokens']} total tokens")
                
            except Exception as e:
                print(f"❌ Failed: {e}")
            
            print("\n")

if __name__ == "__main__":
    test_hybrid_approach() 