#!/usr/bin/env python3
"""
Debug Log Checker - Following Critical Development Rule #3

This script demonstrates how to check debug logs when errors occur.
"""

import requests
import json
import sys
from datetime import datetime


def check_recent_errors(base_url=None, count=10):
    """Check recent errors from the debug endpoint."""
    if base_url is None:
        base_url = "http://localhost:4000"
    try:
        response = requests.get(f"{base_url}/debug/errors/recent", params={"count": count})
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Found {data['count']} recent errors")
            print(f"📁 Log file: {data['log_file']}")
            print("-" * 80)
            
            for i, error in enumerate(data['errors']):
                print(f"\n🔴 Error {i+1}:")
                print(f"  Timestamp: {error['timestamp']}")
                print(f"  Correlation ID: {error['correlation_id']}")
                print(f"  Error Type: {error['error_type']}")
                print(f"  Error Message: {error['error_message']}")
                
                if error.get('context'):
                    print(f"  Service: {error['context'].get('service', 'Unknown')}")
                    print(f"  Method: {error['context'].get('method', 'Unknown')}")
                
                if error.get('request'):
                    print(f"  Request Model: {error['request'].get('model', 'Unknown')}")
                    print(f"  Request API Base: {error['request'].get('api_base', 'Unknown')}")
                
                print("-" * 40)
        else:
            print(f"❌ Failed to fetch errors: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to debug endpoint: {e}")
        print("💡 Make sure the server is running with debug endpoints enabled")


def check_specific_error(correlation_id, base_url=None):
    """Check a specific error by correlation ID."""
    if base_url is None:
        base_url = "http://localhost:4000"
    try:
        response = requests.get(f"{base_url}/debug/errors/{correlation_id}")
        if response.status_code == 200:
            error = response.json()
            if error:
                print(f"\n🔍 Found error with correlation ID: {correlation_id}")
                print(json.dumps(error, indent=2))
            else:
                print(f"❌ No error found with correlation ID: {correlation_id}")
        else:
            print(f"❌ Failed to fetch error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to debug endpoint: {e}")


def check_error_stats(base_url="http://localhost:4000"):
    """Check error statistics."""
    try:
        response = requests.get(f"{base_url}/debug/errors/stats")
        if response.status_code == 200:
            stats = response.json()
            print("\n📈 Error Statistics:")
            print(f"  Total Errors: {stats['total_errors']}")
            
            if stats['time_range']['oldest']:
                print(f"  Time Range: {stats['time_range']['oldest']} to {stats['time_range']['newest']}")
            
            print("\n  Error Types:")
            for error_type, count in stats['error_types'].items():
                print(f"    - {error_type}: {count}")
            
            print("\n  Error Services:")
            for service, count in stats['error_services'].items():
                print(f"    - {service}: {count}")
            
            print("\n  Error Endpoints:")
            for endpoint, count in stats['error_endpoints'].items():
                print(f"    - {endpoint}: {count}")
        else:
            print(f"❌ Failed to fetch error stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to debug endpoint: {e}")


def main():
    """Main function demonstrating Critical Rule #3."""
    print("🚨 CRITICAL DEVELOPMENT RULE #3: CHECK DEBUG LOGS FIRST")
    print("=" * 80)
    print("When ERROR happens, the first thing to do is check the debug log\n")
    
    if len(sys.argv) > 1:
        # Check specific error by correlation ID
        correlation_id = sys.argv[1]
        print(f"Checking specific error: {correlation_id}")
        check_specific_error(correlation_id)
    else:
        # Show recent errors and stats
        print("1️⃣ Checking recent errors...")
        check_recent_errors(count=5)
        
        print("\n2️⃣ Checking error statistics...")
        check_error_stats()
        
        print("\n💡 To check a specific error, run:")
        print("   python check_debug_logs.py <correlation_id>")
        print("\n💡 Example from the logs:")
        print("   python check_debug_logs.py f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation")


if __name__ == "__main__":
    main() 