from neo4j import GraphDatabase
import os

# Neo4j Configuration - loaded from .env file
# Make sure load_dotenv() is called BEFORE importing this module
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Debug: Print configuration (remove in production)
print(f"🔧 Neo4j Configuration:")
print(f"   URI: {NEO4J_URI}")
print(f"   User: {NEO4J_USER}")
print(f"   Password: {'*' * len(NEO4J_PASSWORD) if NEO4J_PASSWORD else 'NOT SET'}")

# For production, use environment variables:
# NEO4J_URI=bolt://your-server:7687
# NEO4J_USER=your-username
# NEO4J_PASSWORD=your-password

driver = None

def get_driver():
    """
    Returns a singleton Neo4j driver instance.
    The driver connects to your existing Sefaria Neo4j database with:
    - 727,309 nodes (Author, Category, Concept, Event, Text, Tradition, Version, Work)
    - 1,258,688 relationships (BELONGS_TO, CITES, COMMENTARY_ON, EXPLICIT, etc.)
    """
    global driver
    if not driver:
        try:
            driver = GraphDatabase.driver(
                NEO4J_URI, 
                auth=(NEO4J_USER, NEO4J_PASSWORD),
                max_connection_lifetime=3600
            )
            # Test connection
            with driver.session() as session:
                session.run("RETURN 1")
            print(f"✅ Connected to Neo4j at {NEO4J_URI}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            print(f"URI: {NEO4J_URI}, User: {NEO4J_USER}")
            raise
    return driver

def close_driver():
    """Close the Neo4j driver connection."""
    global driver
    if driver:
        driver.close()
        driver = None
