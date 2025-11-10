"""
Initialize Sugya nodes in Neo4j database
Creates Sugya nodes for major Talmudic passages
"""
import os
os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI", "neo4j+s://8260863b.databases.neo4j.io")
os.environ["NEO4J_USER"] = os.getenv("NEO4J_USER", "neo4j")
os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD", "IJYDpas_0uO5jbjB6Upk7uiEn_Gs-nb9vyO3oUH6v5c")

from api.sugya_manager import get_sugya_manager

# Define initial sugyot to create
INITIAL_SUGYOT = [
    {
        "ref": "Berakhot 2a",
        "title": "Time for Evening Shema",
        "summary": "Discussion about the proper time to recite the evening Shema prayer"
    },
    {
        "ref": "Berakhot 2b",
        "title": "Recitation of Shema",
        "summary": "Continuation of the discussion about Shema and its proper recitation"
    },
    {
        "ref": "Berakhot 3a",
        "title": "Night Watches",
        "summary": "Discussion about the divisions of the night and when one may recite Shema"
    },
    {
        "ref": "Berakhot 3b",
        "title": "Midnight Study",
        "summary": "Stories about Torah scholars who studied at midnight"
    },
    {
        "ref": "Berakhot 10a",
        "title": "Blessing God",
        "summary": "Discussion about blessing God with one's whole soul"
    },
    {
        "ref": "Berakhot 10b",
        "title": "Torah and Blessings",
        "summary": "The relationship between Torah study and reciting blessings"
    },
]

def main():
    print("=" * 80)
    print("INITIALIZING SUGYOT IN NEO4J DATABASE")
    print("=" * 80)
    
    manager = get_sugya_manager()
    
    created = 0
    for sugya_data in INITIAL_SUGYOT:
        print(f"\nCreating: {sugya_data['ref']}")
        print(f"  Title: {sugya_data['title']}")
        
        try:
            success = manager.create_sugya_node(
                sugya_data['ref'],
                sugya_data['title'],
                sugya_data['summary']
            )
            
            if success:
                print(f"  ✅ Created successfully")
                created += 1
            else:
                print(f"  ❌ Failed to create")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print(f"INITIALIZATION COMPLETE - Created {created}/{len(INITIAL_SUGYOT)} sugyot")
    print("=" * 80)
    
    # List all sugyot to verify
    print("\nVerifying - All available sugyot:")
    all_sugyot = manager.list_all_sugyot()
    for sugya in all_sugyot[:10]:
        print(f"  - {sugya['ref']}: {sugya['title']}")
    
    if len(all_sugyot) > 10:
        print(f"  ... and {len(all_sugyot) - 10} more")

if __name__ == "__main__":
    main()

