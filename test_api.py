#!/usr/bin/env python3
"""Test script for Guard Owl API"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code} - {response.json()}")

def test_queries():
    """Test various queries"""
    queries = [
        {
            "query": "What happened at Site S01 last night?",
            "siteId": "S01"
        },
        {
            "query": "Show me all incidents involving a red Toyota Camry"
        },
        {
            "query": "Were there any geofence breaches this week?",
            "dateRange": {"start": "2025-08-25", "end": "2025-09-03"}
        }
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query['query']}")
        
        response = requests.post(f"{BASE_URL}/query", json=query)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Testing Guard Owl API...")
    
    try:
        test_health()
        test_queries()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on localhost:8000")
        print("Run: python -m uvicorn src.main:app --reload")