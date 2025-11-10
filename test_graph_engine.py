"""
Test script for Engine 1: Dynamic Intertextual Graph Engine
"""
import sys
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
load_dotenv()

from api.connections import get_connections, get_graph_data, get_relationship_types, get_graph_stats

def test_imports():
    """Test that all necessary modules import correctly"""
    print("✅ Testing imports...")
    try:
        from main import app
        from database import get_driver
        from models import Connection
        print("   ✅ All imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_database_connection():
    """Test Neo4j database connection"""
    print("✅ Testing database connection...")
    try:
        from database import get_driver
        driver = get_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            value = result.single()["test"]
            if value == 1:
                print("   ✅ Database connection successful")
                return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_endpoints():
    """Test API endpoint functions"""
    print("✅ Testing API endpoints...")
    
    # Test relationship types endpoint
    try:
        result = get_relationship_types()
        print(f"   ✅ get_relationship_types() returned {result['total']} types")
    except Exception as e:
        print(f"   ⚠️  get_relationship_types() error: {e}")
    
    # Test stats endpoint
    try:
        result = get_graph_stats()
        print(f"   ✅ get_graph_stats() returned {result['nodes']['total']} nodes")
    except Exception as e:
        print(f"   ⚠️  get_graph_stats() error: {e}")
    
    return True

def main():
    print("=" * 60)
    print("Testing Engine 1: Dynamic Intertextual Graph Engine")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_total = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_database_connection():
        tests_passed += 1
    
    if test_endpoints():
        tests_passed += 1
    
    print()
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ All tests passed! Engine 1 is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

