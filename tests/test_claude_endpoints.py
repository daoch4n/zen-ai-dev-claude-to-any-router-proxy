#!/usr/bin/env python3
"""
Test script for Anthropic Claude models on Azure Databricks
Based on: https://devblogs.microsoft.com/all-things-azure/getting-started-with-claude-3-7-sonnet-on-azure-databricks/
"""

import requests
import base64
import json
import os
from typing import Dict, Any, Optional

class ClaudeEndpointTester:
    def __init__(self, workspace_instance: str, databricks_token: str):
        """
        Initialize the Claude endpoint tester.
        
        Args:
            workspace_instance: Your Azure Databricks workspace instance (e.g., 'adb-1234567890123456.7')
            databricks_token: Your Databricks Personal Access Token (PAT)
        """
        self.workspace_instance = workspace_instance
        self.databricks_token = databricks_token
        self.base_url = f"https://{workspace_instance}.azuredatabricks.net/serving-endpoints"
        
        # Azure Databricks uses Basic auth with base64 encoded "token:{PAT}"
        # As per: https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat
        self.auth_header = base64.b64encode(f"token:{databricks_token}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth_header}',
            'Content-Type': 'application/json'
        }
        
    def test_endpoint(self, endpoint_name: str, prompt: str, max_tokens: int = 1000) -> Optional[Dict[Any, Any]]:
        """
        Test a specific Claude endpoint with a given prompt.
        
        Args:
            endpoint_name: Name of the endpoint (e.g., 'databricks-claude-3-7-sonnet')
            prompt: The prompt to send to the model
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Response from the API or None if failed
        """
        print(f"\n{'='*60}")
        print(f"Testing endpoint: {endpoint_name}")
        print(f"Prompt: {prompt}")
        print(f"Method: Azure Databricks API (Basic Auth)")
        print(f"{'='*60}")
        
        return self._test_with_databricks_api(endpoint_name, prompt, max_tokens)
    
    def _test_with_databricks_api(self, endpoint_name: str, prompt: str, max_tokens: int) -> Optional[Dict[Any, Any]]:
        """Test endpoint using Azure Databricks API with proper authentication."""
        url = f"{self.base_url}/{endpoint_name}/invocations"
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        print(f"URL: {url}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success with Azure Databricks API!")
                
                # Extract and display the response content
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', 'No content found')
                    print(f"Response: {content}")
                elif 'content' in result:
                    print(f"Response: {result['content']}")
                else:
                    print(f"Raw response: {json.dumps(result, indent=2)}")
                
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Error text: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return None

def main():
    """Main function to run the endpoint tests."""
    
    # Configuration - Update these values
    WORKSPACE_INSTANCE = os.getenv("DATABRICKS_HOST")   # Replace with your workspace instance
    DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")  # Set this environment variable    

    # Check if required environment variables are set
    if not DATABRICKS_TOKEN or not WORKSPACE_INSTANCE:
        print("❌ Error: DATABRICKS_HOST and DATABRICKS_TOKEN environment variables are required!")
        print("Please set them in your .env file or export them:")
        print("export DATABRICKS_HOST='your-workspace-host.azuredatabricks.net'")
        print("export DATABRICKS_TOKEN='your-databricks-token'")
        print("\nSee .env.example for the expected format.")
        return
    
    # Initialize tester
    tester = ClaudeEndpointTester(WORKSPACE_INSTANCE, DATABRICKS_TOKEN)
    
    # Test prompts
    test_prompts = [
        "Hello! Can you tell me about Azure Databricks?",
        "How is Azure Databricks billed?",
        "What are the key features of Claude AI?",
        "Explain the difference between Claude 3.7 Sonnet and Claude Sonnet 4 in simple terms."
    ]
    
    # Available endpoints to test
    endpoints = [
        "databricks-claude-3-7-sonnet",
        "databricks-claude-sonnet-4"
    ]
    
    print("🚀 Starting Claude API endpoint tests...")
    print(f"Workspace: {WORKSPACE_INSTANCE}")
    
    # Test each endpoint with each prompt
    for endpoint in endpoints:
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🔍 Test {i}/{len(test_prompts)} for {endpoint}")
            result = tester.test_endpoint(endpoint, prompt)
            
            if result:
                print("✅ Test passed")
            else:
                print("❌ Test failed")
            
            # Add a small delay between requests to be respectful
            import time
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print("🏁 All tests completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 