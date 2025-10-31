"""
Enhanced AI API with real implementations
Requires OPENAI_API_KEY in environment
"""

from fastapi import APIRouter, HTTPException
from models import AICommentary
from pydantic import BaseModel
from typing import List
import sys
import os

# Add ai module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

router = APIRouter()

class AICommentaryRequest(BaseModel):
    text_ref: str
    tradition: str = "Rashi"
    mode: str = "pshat"

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10

@router.get("/ai-enhanced/commentary/{text_ref}", response_model=AICommentary)
async def get_ai_commentary(text_ref: str, tradition: str = "Rashi", mode: str = "pshat"):
    """
    Get AI-generated commentary for a text.
    Supports traditions: Rashi, Ramban, Ibn Ezra, Sforno, Maharal
    Modes: pshat, halakhah, mystical, homiletical
    
    Will try to get text from Neo4j, but can generate from text_ref alone if needed.
    """
    try:
        # Import here to avoid circular dependencies
        from ai.commentary_generator import CommentaryGenerator
        from database import get_driver
        
        generator = CommentaryGenerator()
        
        # Check cache first
        cached = await generator.get_cached_commentary(text_ref, tradition, mode)
        if cached:
            print(f"✅ Returning cached commentary for {text_ref}")
            return AICommentary(
                text_ref=text_ref,
                tradition=tradition,
                mode=mode,
                generated=cached
            )
        
        # Try to get text from database, but don't fail if not found
        text_content = None
        driver = get_driver()
        try:
            with driver.session() as session:
                # Use OPTIONAL MATCH - won't fail if Text node doesn't exist
                result = session.run("""
                    OPTIONAL MATCH (t:Text {id: $text_ref})
                    RETURN coalesce(t.content_he, t.content_en, '') as content
                """, {"text_ref": text_ref}).single()
                
                if result and result["content"]:
                    text_content = result["content"]
                    print(f"✅ Found text in database for {text_ref}")
        except Exception as db_error:
            print(f"⚠️ Database lookup failed (continuing anyway): {db_error}")
        
        # If no text found in database, use the reference itself for commentary
        if not text_content:
            print(f"ℹ️ No text in database for {text_ref} - generating commentary on reference")
            text_content = f"Biblical reference: {text_ref}"
        
        # Generate commentary
        commentary = await generator.generate(
            text=text_content,
            text_ref=text_ref,
            tradition=tradition,
            mode=mode
        )
        
        return AICommentary(
            text_ref=text_ref,
            tradition=tradition,
            mode=mode,
            generated=commentary
        )
        
    except Exception as e:
        # Fallback to error message
        print(f"❌ Error generating commentary: {e}")
        return AICommentary(
            text_ref=text_ref,
            tradition=tradition,
            mode=mode,
            generated=f"Error generating commentary: {str(e)}"
        )

@router.post("/ai-enhanced/commentary/", response_model=AICommentary)
async def ai_commentary_post(payload: AICommentaryRequest):
    """Generate AI commentary via POST with request body"""
    return await get_ai_commentary(
        text_ref=payload.text_ref,
        tradition=payload.tradition,
        mode=payload.mode
    )

@router.post("/ai-enhanced/semantic-search/")
async def semantic_search(request: SemanticSearchRequest):
    """
    Semantic search across all texts using embeddings.
    Requires texts to be embedded first (see /ai-enhanced/embed endpoint).
    """
    try:
        from ai.embeddings import SemanticSearch
        
        searcher = SemanticSearch()
        results = await searcher.search(request.query, request.limit)
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search error: {str(e)}")

@router.post("/ai-enhanced/embed-batch/")
async def embed_batch_texts(batch_size: int = 100):
    """
    Embed a batch of texts (requires OPENAI_API_KEY).
    This is a background task that should be run periodically.
    """
    try:
        from ai.embeddings import TextEmbedder
        
        embedder = TextEmbedder()
        count = await embedder.batch_embed_texts(batch_size)
        
        return {
            "message": f"Successfully embedded {count} texts",
            "batch_size": batch_size,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

@router.get("/ai-enhanced/similar-texts/{text_id}")
async def find_similar_texts(text_id: str, limit: int = 10):
    """Find texts semantically similar to the given text"""
    try:
        from ai.embeddings import SemanticSearch
        
        searcher = SemanticSearch()
        results = await searcher.find_similar_texts(text_id, limit)
        
        return {
            "source_text_id": text_id,
            "similar_texts": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar texts: {str(e)}")

@router.post("/ai-enhanced/extract-citations/")
async def extract_citations(text: str):
    """Extract halakhic citations from text using AI"""
    try:
        from ai.commentary_generator import CitationExtractor
        
        extractor = CitationExtractor()
        citations = await extractor.extract_citations(text)
        
        return {
            "text": text[:200] + "..." if len(text) > 200 else text,
            "citations": citations,
            "count": len(citations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Citation extraction error: {str(e)}")

