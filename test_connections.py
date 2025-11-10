#!/usr/bin/env python3
"""
Test script for Neo4j connections API
Run this to verify the backend connections are working without deprecation warnings
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, expected_status=200):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ SUCCESS")
            data = response.json()
            print(f"\nResponse preview:")
            print(json.dumps(data, indent=2)[:500] + "...")
            return True
        else:
            print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("="*60)
    print("Neo4j Connections API Test Suite")
    print("="*60)
    print("\nMake sure the backend server is running on http://localhost:8000")
    print("Press Ctrl+C to exit\n")
    
    # Test node IDs - adjust these to match your database
    test_nodes = [
        "Genesis 2:2",
        "Berakhot 2a",
        "Genesis 1:1"
    ]
    
    results = []
    
    # Test 1: Health check (if available)
    print("\n" + "="*60)
    print("1. Testing Backend Health")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("⚠️  Backend health check returned:", response.status_code)
    except:
        print("⚠️  Could not reach backend - make sure it's running")
        print("   Start with: cd backend && uvicorn main:app --reload")
        sys.exit(1)
    
    # Test 2: Get relationship types
    print("\n" + "="*60)
    print("2. Testing Relationship Types Endpoint")
    print("="*60)
    
    result = test_endpoint(
        "Get Relationship Types",
        f"{BASE_URL}/api/connections/relationship-types"
    )
    results.append(("Relationship Types", result))
    
    # Test 3: Get graph stats
    print("\n" + "="*60)
    print("3. Testing Graph Stats Endpoint")
    print("="*60)
    
    result = test_endpoint(
        "Get Graph Stats",
        f"{BASE_URL}/api/connections/stats"
    )
    results.append(("Graph Stats", result))
    
    # Test 4: Get connections for each test node
    for i, node_id in enumerate(test_nodes, start=4):
        print("\n" + "="*60)
        print(f"{i}. Testing Connections for: {node_id}")
        print("="*60)
        
        result = test_endpoint(
            f"Connections: {node_id}",
            f"{BASE_URL}/api/connections/{requests.utils.quote(node_id)}?limit=10",
            expected_status=200  # or 404 if node doesn't exist
        )
        results.append((f"Connections: {node_id}", result))
    
    # Test 5: Get graph data
    test_node = test_nodes[0]
    print("\n" + "="*60)
    print(f"5. Testing Graph Data for: {test_node}")
    print("="*60)
    
    result = test_endpoint(
        f"Graph Data: {test_node}",
        f"{BASE_URL}/api/connections/graph/{requests.utils.quote(test_node)}?depth=2&limit=50",
        expected_status=200  # or 404 if node doesn't exist
    )
    results.append((f"Graph Data: {test_node}", result))
    
    # Test 6: Get graph data with relationship filter
    print("\n" + "="*60)
    print(f"6. Testing Graph Data with Filter: {test_node}")
    print("="*60)
    
    result = test_endpoint(
        f"Graph Data (CITES): {test_node}",
        f"{BASE_URL}/api/connections/graph/{requests.utils.quote(test_node)}?depth=2&relationship_type=CITES",
        expected_status=200  # or 404 if no results
    )
    results.append((f"Graph Data (Filtered): {test_node}", result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! No deprecation warnings should appear in logs.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "="*60)
    print("IMPORTANT: Check the backend server logs for deprecation warnings")
    print("You should NOT see any warnings about:")
    print("  - 'id is deprecated'")
    print("  - 'property key does not exist: <id>'")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)

