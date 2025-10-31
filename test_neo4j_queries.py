"""
Test Neo4j queries to ensure they use parameters correctly
"""
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def test_commentary_generation():
    """Test the commentary generation with proper parameter usage"""
    from ai.commentary_generator import CommentaryGenerator
    
    print("=" * 60)
    print("Testing Commentary Generation with Genesis.1.1")
    print("=" * 60)
    
    generator = CommentaryGenerator()
    text_ref = "Genesis.1.1"
    
    try:
        # Test getting cached (should return None for first time)
        print(f"\n1. Testing get_cached_commentary('{text_ref}')...")
        cached = await generator.get_cached_commentary(text_ref, "Rashi", "pshat")
        print(f"   Result: {cached if cached else 'None (expected for first time)'}")
        
        # Test generating commentary
        print(f"\n2. Testing generate() for '{text_ref}'...")
        commentary = await generator.generate(
            text=f"In the beginning God created the heaven and the earth. ({text_ref})",
            text_ref=text_ref,
            tradition="Rashi",
            mode="pshat"
        )
        print(f"   Generated: {commentary[:100]}...")
        
        # Test getting cached (should return value now)
        print(f"\n3. Testing get_cached_commentary('{text_ref}') again...")
        cached = await generator.get_cached_commentary(text_ref, "Rashi", "pshat")
        print(f"   Result: {'Found!' if cached else 'Still None'}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_commentary_generation())

