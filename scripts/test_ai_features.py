"""
Test script for AI features
Tests commentary generation, semantic search, and embeddings
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.commentary_generator import CommentaryGenerator
from ai.embeddings import SemanticSearch, TextEmbedder
from database import get_driver

async def test_commentary():
    """Test AI commentary generation"""
    print("\n" + "=" * 60)
    print("🔬 Testing AI Commentary Generation")
    print("=" * 60)
    
    generator = CommentaryGenerator()
    
    # Get a sample text from database
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Text)
            WHERE t.content_he IS NOT NULL
            RETURN t.id as ref, t.content_he as content
            LIMIT 1
        """).single()
        
        if not result:
            print("❌ No texts found in database")
            return
        
        text_ref = result["ref"]
        content = result["content"][:500]  # First 500 chars
    
    print(f"\n📖 Text Reference: {text_ref}")
    print(f"📝 Content: {content[:100]}...")
    print()
    
    # Generate commentary
    print("Generating Rashi-style commentary...")
    commentary = await generator.generate(
        text=content,
        text_ref=text_ref,
        tradition="Rashi",
        mode="pshat"
    )
    
    print("\n💬 Generated Commentary:")
    print("-" * 60)
    print(commentary)
    print("-" * 60)
    
    return True

async def test_semantic_search():
    """Test semantic search"""
    print("\n" + "=" * 60)
    print("🔍 Testing Semantic Search")
    print("=" * 60)
    
    searcher = SemanticSearch()
    
    query = "divine kindness and mercy"
    print(f"\n🔎 Query: '{query}'")
    print()
    
    results = await searcher.search(query, limit=5)
    
    if not results:
        print("❌ No results found. Make sure texts are embedded first!")
        print("   Run: python scripts/embed_texts.py")
        return False
    
    print(f"✅ Found {len(results)} results:")
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   Ref: {result.get('text_ref', 'N/A')}")
        print(f"   Content: {result.get('content', '')[:100]}...")
        print()
    
    return True

async def test_embeddings():
    """Test embedding generation"""
    print("\n" + "=" * 60)
    print("🧬 Testing Embedding Generation")
    print("=" * 60)
    
    embedder = TextEmbedder()
    
    # Get count of embedded texts
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Text) 
            WHERE t.embedding IS NOT NULL 
            RETURN count(t) as count
        """).single()
        
        embedded_count = result["count"]
    
    print(f"\n📊 Embedded texts: {embedded_count:,}")
    
    if embedded_count == 0:
        print("\n⚠️  No texts embedded yet. Embedding a sample text...")
        
        # Embed one text as test
        with driver.session() as session:
            result = session.run("""
                MATCH (t:Text)
                WHERE t.embedding IS NULL 
                      AND t.content_he IS NOT NULL
                RETURN t.`<id>` as id, t.content_he as content
                LIMIT 1
            """).single()
            
            if result:
                success = await embedder.embed_and_store(
                    result["id"],
                    result["content"]
                )
                
                if success:
                    print("✅ Successfully embedded sample text!")
                else:
                    print("❌ Failed to embed text")
                    return False
    
    return True

async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 AI FEATURES TEST SUITE")
    print("=" * 70)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY not set!")
        print("Please add your OpenAI API key to .env file")
        return
    
    print("\n✅ OpenAI API key found")
    
    # Run tests
    tests = [
        ("Embeddings", test_embeddings),
        ("Commentary Generation", test_commentary),
        ("Semantic Search", test_semantic_search),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result if result is not None else True
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print()
    all_passed = all(results.values())
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check errors above.")

if __name__ == "__main__":
    asyncio.run(main())

