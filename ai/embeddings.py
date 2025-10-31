"""
Text Embedding System for Semantic Search
Generates and manages vector embeddings for all texts in Neo4j
"""

from openai import OpenAI
from database import get_driver
import os
from typing import List, Optional
import asyncio

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug: Check if API key is loaded (remove in production)
if OPENAI_API_KEY:
    print(f"✅ OpenAI API key loaded for embeddings (length: {len(OPENAI_API_KEY)})")
else:
    print("⚠️ WARNING: OPENAI_API_KEY not found - embeddings will not work!")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class TextEmbedder:
    def __init__(self):
        self.model = "text-embedding-3-large"  # 1536 dimensions
        self.max_tokens = 8000
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        # Check if OpenAI client is available
        if not client:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in .env file.")
        
        try:
            response = client.embeddings.create(
                model=self.model,
                input=text[:self.max_tokens]
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    async def embed_and_store(self, node_id: str, content: str):
        """Generate embedding and store in Neo4j"""
        embedding = await self.embed_text(content)
        
        if not embedding:
            return False
        
        driver = get_driver()
        try:
            with driver.session() as session:
                session.run("""
                    MATCH (t:Text {`<id>`: $node_id})
                    SET t.embedding = $embedding,
                        t.embedding_model = $model,
                        t.embedded_at = datetime()
                """, {
                    "node_id": node_id,
                    "embedding": embedding,
                    "model": self.model
                })
            return True
        except Exception as e:
            print(f"Error storing embedding: {e}")
            return False
    
    async def batch_embed_texts(self, batch_size: int = 100):
        """Embed all texts in batches"""
        driver = get_driver()
        
        with driver.session() as session:
            # Get texts without embeddings
            result = session.run("""
                MATCH (t:Text)
                WHERE t.embedding IS NULL
                RETURN t.`<id>` as id, 
                       coalesce(t.content_he, t.content_en, '') as content
                LIMIT $batch_size
            """, {"batch_size": batch_size})
            
            texts = list(result)
            
            if not texts:
                print("No texts to embed")
                return 0
            
            print(f"Embedding {len(texts)} texts...")
            
            embedded_count = 0
            for record in texts:
                if record["content"]:
                    success = await self.embed_and_store(
                        record["id"],
                        record["content"]
                    )
                    if success:
                        embedded_count += 1
            
            return embedded_count

class SemanticSearch:
    """Semantic search using vector similarity"""
    
    def __init__(self):
        self.embedder = TextEmbedder()
    
    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Find texts semantically similar to query"""
        
        # Generate query embedding
        query_embedding = await self.embedder.embed_text(query)
        
        if not query_embedding:
            return []
        
        driver = get_driver()
        try:
            with driver.session() as session:
                # Use Neo4j vector similarity search
                results = session.run("""
                    MATCH (t:Text)
                    WHERE t.embedding IS NOT NULL
                    WITH t, 
                         gds.similarity.cosine(t.embedding, $query_embedding) AS score
                    WHERE score > 0.7
                    RETURN t.`<id>` as id,
                           t.id as text_ref,
                           coalesce(t.content_he, t.content_en) as content,
                           score
                    ORDER BY score DESC
                    LIMIT $limit
                """, {
                    "query_embedding": query_embedding,
                    "limit": limit
                })
                
                return [dict(record) for record in results]
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    async def find_similar_texts(self, text_id: str, limit: int = 10) -> List[dict]:
        """Find texts similar to a given text"""
        driver = get_driver()
        
        try:
            with driver.session() as session:
                # Get embedding of source text
                source = session.run("""
                    MATCH (t:Text {`<id>`: $text_id})
                    RETURN t.embedding as embedding
                """, {"text_id": text_id}).single()
                
                if not source or not source["embedding"]:
                    return []
                
                source_embedding = source["embedding"]
                
                # Find similar texts
                results = session.run("""
                    MATCH (t:Text)
                    WHERE t.`<id>` <> $text_id 
                          AND t.embedding IS NOT NULL
                    WITH t,
                         gds.similarity.cosine(t.embedding, $source_embedding) AS score
                    WHERE score > 0.8
                    RETURN t.`<id>` as id,
                           t.id as text_ref,
                           coalesce(t.content_he, t.content_en) as content,
                           score
                    ORDER BY score DESC
                    LIMIT $limit
                """, {
                    "text_id": text_id,
                    "source_embedding": source_embedding,
                    "limit": limit
                })
                
                return [dict(record) for record in results]
        except Exception as e:
            print(f"Error finding similar texts: {e}")
            return []

