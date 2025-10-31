"""
Script to batch embed all texts in the Neo4j database
Run this to generate embeddings for semantic search
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.embeddings import TextEmbedder
from database import get_driver

async def main():
    """Main embedding process"""
    print("🚀 Starting text embedding process...")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not set in environment!")
        print("Please add your OpenAI API key to .env file:")
        print("OPENAI_API_KEY=sk-your-key-here")
        return
    
    # Get total count of texts
    driver = get_driver()
    with driver.session() as session:
        result = session.run("MATCH (t:Text) RETURN count(t) as total").single()
        total_texts = result["total"]
        
        result = session.run("""
            MATCH (t:Text) 
            WHERE t.embedding IS NOT NULL 
            RETURN count(t) as embedded
        """).single()
        already_embedded = result["embedded"]
    
    remaining = total_texts - already_embedded
    
    print(f"📊 Database Statistics:")
    print(f"   Total texts: {total_texts:,}")
    print(f"   Already embedded: {already_embedded:,}")
    print(f"   Remaining: {remaining:,}")
    print()
    
    if remaining == 0:
        print("✅ All texts are already embedded!")
        return
    
    # Estimate cost
    avg_tokens_per_text = 500
    cost_per_1k_tokens = 0.00013
    estimated_cost = (remaining * avg_tokens_per_text * cost_per_1k_tokens) / 1000
    
    print(f"💰 Estimated Cost:")
    print(f"   ~${estimated_cost:.2f} to embed {remaining:,} texts")
    print()
    
    # Ask for confirmation
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Cancelled")
        return
    
    print()
    print("🔄 Starting embedding process...")
    print("This will take a while. Progress will be shown below.")
    print("=" * 60)
    print()
    
    embedder = TextEmbedder()
    total_embedded = 0
    batch_size = 100
    
    while True:
        print(f"Processing batch {total_embedded // batch_size + 1}...")
        
        count = await embedder.batch_embed_texts(batch_size)
        
        if count == 0:
            print()
            print("✅ All texts embedded!")
            break
        
        total_embedded += count
        progress = (already_embedded + total_embedded) / total_texts * 100
        
        print(f"   Embedded {count} texts")
        print(f"   Total progress: {already_embedded + total_embedded:,}/{total_texts:,} ({progress:.1f}%)")
        print()
        
        # Small delay to avoid rate limits
        await asyncio.sleep(1)
    
    print("=" * 60)
    print(f"🎉 Embedding complete!")
    print(f"   Total embedded in this session: {total_embedded:,}")
    print(f"   Database now has: {already_embedded + total_embedded:,} embedded texts")

if __name__ == "__main__":
    asyncio.run(main())

