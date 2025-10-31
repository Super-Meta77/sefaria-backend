"""
Quick test to verify environment variables are loaded correctly
Run this before starting the main application to verify configuration
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 60)
print("ENVIRONMENT VARIABLE CHECK")
print("=" * 60)

# Check Neo4j configuration
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")
openai_key = os.getenv("OPENAI_API_KEY")

print("\n1. Neo4j Configuration:")
print(f"   URI: {neo4j_uri}")
print(f"   User: {neo4j_user}")
print(f"   Password: {'*' * len(neo4j_password) if neo4j_password else 'NOT SET'}")

print("\n2. OpenAI Configuration:")
if openai_key:
    print(f"   API Key: {'*' * (len(openai_key) - 8) + openai_key[-8:]}")
    print(f"   Key length: {len(openai_key)} characters")
else:
    print("   ❌ API Key: NOT SET")

print("\n3. Testing Neo4j Connection:")
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_user, neo4j_password),
        max_connection_lifetime=3600
    )
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        test_value = result.single()["test"]
        if test_value == 1:
            print("   ✅ Neo4j connection successful!")
        driver.close()
except Exception as e:
    print(f"   ❌ Neo4j connection failed: {str(e)}")

print("\n4. Testing OpenAI Configuration:")
try:
    if openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        # Don't make an actual API call, just check if client initializes
        print("   ✅ OpenAI client initialized successfully!")
    else:
        print("   ❌ Cannot test OpenAI - API key not set")
except Exception as e:
    print(f"   ❌ OpenAI initialization failed: {str(e)}")

print("\n" + "=" * 60)
print("CONFIGURATION CHECK COMPLETE")
print("=" * 60)

