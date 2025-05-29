#!/usr/bin/env python3
"""
Test the OpenRouter to Anthropic Server
"""

import requests
import json

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get("http://localhost:5001/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data.get('status')}")
            return True
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False

def test_anthropic_sdk():
    """Test with Anthropic SDK"""
    print("\n🔍 Testing with Anthropic SDK...")
    try:
        from anthropic import Anthropic
        
        client = Anthropic(
            api_key="dummy-key",
            base_url="http://localhost:5001"
        )
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Claude Code default
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Hello! Please respond briefly."}
            ]
        )
        
        print(f"✅ SDK Response:")
        print(f"   ID: {message.id}")
        print(f"   Model: {message.model}")
        print(f"   Content: {message.content[0].text}")
        print(f"   Usage: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
        return True
        
    except ImportError:
        print("❌ Anthropic SDK not installed")
        return False
    except Exception as e:
        print(f"❌ SDK Error: {e}")
        return False

def test_raw_request():
    """Test with raw HTTP request"""
    print("\n🔍 Testing Raw HTTP Request...")
    try:
        payload = {
            "model": "claude-3-7-sonnet-20250219",  # Claude Code Amazon Bedrock default
            "max_tokens": 50,
            "messages": [
                {"role": "user", "content": "Hello! Please respond briefly."}
            ]
        }
        
        response = requests.post(
            "http://localhost:5001/v1/messages",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Raw Response:")
            print(f"   ID: {data['id']}")
            print(f"   Type: {data['type']}")
            print(f"   Model: {data['model']}")
            print(f"   Content: {data['content'][0]['text']}")
            print(f"   Usage: {data['usage']['input_tokens']} in, {data['usage']['output_tokens']} out")
            return True
        else:
            print(f"❌ Raw request failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Raw request error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 OpenRouter to Anthropic Server Test")
    print("=" * 50)
    
    results = {}
    results['health'] = test_health()
    results['anthropic_sdk'] = test_anthropic_sdk()
    results['raw_request'] = test_raw_request()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("✓ Server is working correctly")
        print("✓ Ready for Claude Code integration")
        print("\n📝 Configure Claude Code to use: http://localhost:5001")
    else:
        print("\n⚠️ Some tests failed")

if __name__ == "__main__":
    main()