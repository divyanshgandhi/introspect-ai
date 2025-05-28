#!/usr/bin/env python3
"""
Test script for rate limiting functionality.

This script tests the rate limiting by making multiple requests to the API
and verifying that the rate limit is enforced correctly.
"""

import requests
import time
import json
from typing import Dict, Any


def test_rate_limiting(base_url: str = "http://localhost:8000"):
    """
    Test the rate limiting functionality by making multiple requests.

    Args:
        base_url: Base URL of the API server
    """
    print("🧪 Testing Rate Limiting Functionality")
    print("=" * 50)

    # Test endpoint
    extract_url = f"{base_url}/api/extract"
    status_url = f"{base_url}/api/rate-limit-status"

    # Test data
    test_data = {"youtube_url": "https://www.youtube.com/watch?v=test"}

    print(f"📍 Testing against: {base_url}")
    print(f"📊 Rate limit: 5 requests per 24 hours")
    print()

    # Check initial status
    print("1️⃣ Checking initial rate limit status...")
    try:
        response = requests.get(status_url)
        if response.status_code == 200:
            status = response.json()
            print(
                f"   ✅ Initial status: {status['remaining_requests']}/{status['max_requests']} requests remaining"
            )
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting status: {e}")

    print()

    # Make requests until rate limit is hit
    print("2️⃣ Making requests to test rate limiting...")

    for i in range(1, 8):  # Try to make 7 requests (should fail after 5)
        print(f"   Request {i}:", end=" ")

        try:
            response = requests.post(extract_url, data=test_data)

            # Check rate limit headers
            headers = response.headers
            limit = headers.get("X-RateLimit-Limit", "N/A")
            remaining = headers.get("X-RateLimit-Remaining", "N/A")
            reset = headers.get("X-RateLimit-Reset", "N/A")

            if response.status_code == 200:
                print(f"✅ Success (Remaining: {remaining}/{limit})")
            elif response.status_code == 429:
                print(f"🚫 Rate limited (Remaining: {remaining}/{limit})")
                error_detail = response.json().get("detail", {})
                if isinstance(error_detail, dict):
                    print(
                        f"      Message: {error_detail.get('message', 'Rate limit exceeded')}"
                    )
                    reset_time = error_detail.get("reset_time")
                    if reset_time:
                        print(f"      Reset time: {reset_time}")
                break
            else:
                print(f"❌ Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Request failed: {e}")

        # Small delay between requests
        time.sleep(0.5)

    print()

    # Check final status
    print("3️⃣ Checking final rate limit status...")
    try:
        response = requests.get(status_url)
        if response.status_code == 200:
            status = response.json()
            print(f"   📊 Final status:")
            print(f"      Remaining requests: {status['remaining_requests']}")
            print(f"      Is limited: {status['is_limited']}")
            print(f"      Reset time: {status['reset_time']}")
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting status: {e}")

    print()
    print("✅ Rate limiting test completed!")


def test_different_endpoints(base_url: str = "http://localhost:8000"):
    """
    Test that rate limiting applies across different endpoints.

    Args:
        base_url: Base URL of the API server
    """
    print("\n🔄 Testing Rate Limiting Across Different Endpoints")
    print("=" * 50)

    endpoints = [
        f"{base_url}/api/extract",
        f"{base_url}/api/process",
    ]

    test_data = {
        "youtube_url": "https://www.youtube.com/watch?v=test",
        "interests": "AI and technology",
        "goals": "Learn about rate limiting",
        "background": "Software developer",
    }

    print("Making requests to different endpoints...")

    for i, endpoint in enumerate(endpoints, 1):
        print(f"   Request {i} to {endpoint.split('/')[-1]}:", end=" ")

        try:
            response = requests.post(endpoint, data=test_data)
            remaining = response.headers.get("X-RateLimit-Remaining", "N/A")

            if response.status_code == 200:
                print(f"✅ Success (Remaining: {remaining})")
            elif response.status_code == 429:
                print(f"🚫 Rate limited (Remaining: {remaining})")
                break
            else:
                print(f"❌ Error {response.status_code}")

        except Exception as e:
            print(f"❌ Request failed: {e}")

        time.sleep(0.5)


if __name__ == "__main__":
    import sys

    # Allow custom base URL as command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print("🚀 Starting Rate Limiting Tests")
    print(f"🌐 API Base URL: {base_url}")
    print()

    # Test basic rate limiting
    test_rate_limiting(base_url)

    # Test across different endpoints
    test_different_endpoints(base_url)

    print("\n🎉 All tests completed!")
    print("\n💡 Note: Rate limits are per IP address and reset after 24 hours.")
    print("   To reset for testing, restart the API server.")
