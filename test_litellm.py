#!/usr/bin/env python3
"""
Test script to verify LiteLLM proxy with OpenRouter is working correctly.
This bypasses Claude Code and tests the proxy directly.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_litellm_proxy():
    """Test the LiteLLM proxy endpoint directly"""
    
    # Configuration
    base_url = "http://localhost:4000"
    master_key = os.getenv('LITELLM_MASTER_KEY')
    
    if not master_key:
        print("❌ LITELLM_MASTER_KEY environment variable not set")
        print("   Please set it in your .env file")
        return False
    
    print("🔍 Testing LiteLLM Proxy with OpenRouter...")
    print(f"📍 Base URL: {base_url}")
    print(f"🔑 Master Key: {master_key[:10]}...")
    print("-" * 50)
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Endpoint...")
    try:
        health_response = requests.get(
            f"{base_url}/health",
            headers={"Authorization": f"Bearer {master_key}"},
            timeout=10
        )
        print(f"   Status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Healthy endpoints: {health_data.get('healthy_count', 0)}")
            print(f"   Unhealthy endpoints: {health_data.get('unhealthy_count', 0)}")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {health_response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    print()
    
    # Test 2: Chat Completion
    print("2️⃣ Testing Chat Completion...")
    try:
        chat_payload = {
            "model": "anthropic/claude-sonnet-4",
            "messages": [
                {"role": "user", "content": "What's your name? Please respond briefly."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        chat_response = requests.post(
            f"{base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {master_key}",
                "Content-Type": "application/json"
            },
            json=chat_payload,
            timeout=30
        )
        
        print(f"   Status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            message = chat_data['choices'][0]['message']['content']
            usage = chat_data.get('usage', {})
            
            print(f"   Response: {message}")
            print(f"   Tokens used: {usage.get('total_tokens', 'unknown')}")
            print("   ✅ Chat completion successful")
            return True
        else:
            print(f"   ❌ Chat completion failed: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat completion error: {e}")
        return False

def test_docker_status():
    """Check Docker container status"""
    print("🐳 Checking Docker Container Status...")
    try:
        result = os.popen("docker ps --filter name=litellm-proxy --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'").read()
        print(result)
        
        # Check if container is running
        if "litellm-proxy" in result and "Up" in result:
            print("   ✅ LiteLLM container is running")
            return True
        else:
            print("   ❌ LiteLLM container is not running properly")
            return False
    except Exception as e:
        print(f"   ❌ Docker check error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 LiteLLM Proxy Test Suite")
    print("=" * 50)
    
    # Test Docker status first
    docker_ok = test_docker_status()
    print()
    
    if docker_ok:
        # Test the proxy
        proxy_ok = test_litellm_proxy()
        
        print()
        print("📊 Test Results:")
        print(f"   Docker Status: {'✅ OK' if docker_ok else '❌ FAIL'}")
        print(f"   Proxy Status: {'✅ OK' if proxy_ok else '❌ FAIL'}")
        
        if docker_ok and proxy_ok:
            print("\n🎉 All tests passed! LiteLLM proxy is working correctly.")
            print("   The issue is likely with Claude Code's connection, not the proxy.")
        else:
            print("\n⚠️  Some tests failed. Check the proxy configuration.")
    else:
        print("\n❌ Docker container issues detected. Please check Docker setup.")