#!/usr/bin/env python3
"""
Test script for Anomaly Detection API
"""

import requests
import json

API_BASE = "http://localhost:5001/api/v1"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


# Insider threat removed - only false positive test


def test_false_positive():
    """Test false positive analysis"""
    print("\n=== Testing False Positive Analysis ===")
    payload = {
        "num_events": 100,
        "threat_rate": 0.2,
        "false_positive_rate": 0.15
    }
    response = requests.post(f"{API_BASE}/anomaly/false-positive", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


# Sensor attack removed - only false positive test


# Test all removed - only false positive test


if __name__ == "__main__":
    print("\n" + "="*70)
    print("    ANOMALY DETECTION API - TEST SUITE")
    print("="*70)

    try:
        # Test health first
        test_health()

        # Test false positive only
        test_false_positive()

        print("\n" + "="*70)
        print("    FALSE POSITIVE TEST COMPLETED")
        print("="*70 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server!")
        print("Make sure the server is running: python anomaly_api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
