"""
Test the Sugya API endpoints with real data
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

print("=" * 80)
print("TESTING SUGYA API ENDPOINTS")
print("=" * 80)

# Test 1: List all available sugyot
print("\n1. Testing /api/sugya/list/available")
try:
    response = requests.get(f"{BASE_URL}/sugya/list/available")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success - Found {data['total']} sugyot")
        for sugya in data['sugyot'][:5]:
            print(f"      - {sugya['ref']}: {sugya['title']}")
    else:
        print(f"   ❌ Failed - Status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Get specific sugya structure
print("\n2. Testing /api/sugya/Berakhot 2a")
try:
    response = requests.get(f"{BASE_URL}/sugya/Berakhot%202a")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success")
        print(f"      Title: {data['title']}")
        print(f"      Summary: {data['summary']}")
        print(f"      Root type: {data['root']['type']}")
        print(f"      Children: {len(data['root']['children'])}")
    else:
        print(f"   ❌ Failed - Status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get sugya that doesn't exist
print("\n3. Testing /api/sugya/NonExistent (should 404)")
try:
    response = requests.get(f"{BASE_URL}/sugya/NonExistent")
    if response.status_code == 404:
        print(f"   ✅ Correctly returns 404")
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("API TESTING COMPLETE")
print("=" * 80)
print("\n💡 Start the backend with: uvicorn main:app --reload")
print("💡 View docs at: http://localhost:8000/docs")

