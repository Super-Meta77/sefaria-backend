"""
AI Commentary Generation System
Generates Torah commentary in the style of traditional commentators
"""

from openai import OpenAI
from database import get_driver
import os
from typing import Optional
import json

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug: Check if API key is loaded (remove in production)
if OPENAI_API_KEY:
    print(f"✅ OpenAI API key loaded (length: {len(OPENAI_API_KEY)})")
else:
    print("⚠️ WARNING: OPENAI_API_KEY not found in environment variables!")
    print("   Make sure .env file exists and load_dotenv() is called before importing this module")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class CommentaryGenerator:
    """Generate AI-powered Torah commentary"""
    
    TRADITION_PROMPTS = {
        "Rashi": """You are Rashi (Rabbi Shlomo Yitzchaki, 1040-1105), the preeminent Torah commentator.
Your style:
- Focus on pshat (plain meaning)
- Explain difficult words and phrases
- Cite midrashim when helpful
- Use clear, accessible language
- Often begin with "למה נאמר" (Why is this stated?)
""",
        "Ramban": """You are Ramban (Nachmanides, 1194-1270), a kabbalist and biblical commentator.
Your style:
- Combine pshat with kabbalah
- Challenge Rashi when you disagree
- Provide deep philosophical insights
- Reference mystical traditions
- Synthesize multiple interpretive approaches
""",
        "Ibn Ezra": """You are Ibn Ezra (1089-1167), rationalist Torah commentator.
Your style:
- Emphasize grammatical analysis
- Use logic and reason
- Astronomical and mathematical insights
- Critique interpretations you find unreasonable
- Focus on linguistic precision
""",
        "Sforno": """You are Sforno (Ovadiah ben Jacob, 1475-1550), Italian Torah commentator.
Your style:
- Moralistic interpretations
- Philosophical depth
- Explain Torah's ethical lessons
- Clear, systematic exposition
- Balance between pshat and derash
""",
        "Maharal": """You are Maharal of Prague (1520-1609), mystic and philosopher.
Your style:
- Deep philosophical analysis
- Explain contradictions
- Metaphysical interpretations
- Connect to broader Jewish thought
- Emphasize spiritual meaning
"""
    }
    
    MODE_INSTRUCTIONS = {
        "pshat": "Focus on the plain, literal meaning of the text.",
        "halakhah": "Emphasize halakhic (legal) implications and rulings.",
        "mystical": "Provide kabbalistic and mystical interpretations.",
        "homiletical": "Offer inspiring, moralistic teachings."
    }
    
    def __init__(self):
        self.model = "gpt-4-turbo"
        self.temperature = 0.3
    
    async def get_tradition_examples(self, tradition: str, limit: int = 3) -> str:
        """Fetch real commentary examples from Neo4j if available"""
        driver = get_driver()
        
        try:
            with driver.session() as session:
                # Use OPTIONAL MATCH - won't fail if Author/Text nodes don't exist
                result = session.run("""
                    OPTIONAL MATCH (a:Author)-[:WRITTEN_BY]-(t:Text)
                    WHERE a.name CONTAINS $tradition
                          AND t.content_he IS NOT NULL
                    RETURN t.content_he as content
                    LIMIT $limit
                """, {"tradition": tradition, "limit": limit})
                
                examples = [record["content"][:500] for record in result if record.get("content")]
                
                if examples:
                    print(f"✅ Found {len(examples)} example(s) for {tradition}")
                    return "\n\n---\n\n".join(examples)
                else:
                    print(f"ℹ️ No examples found for {tradition} - will use prompt only")
                    return ""
        except Exception as e:
            print(f"⚠️ Error fetching examples (skipping): {e}")
            return ""
    
    async def generate(
        self,
        text: str,
        text_ref: str,
        tradition: str = "Rashi",
        mode: str = "pshat"
    ) -> str:
        """Generate commentary in specified tradition and mode"""
        
        # Check if OpenAI client is available
        if not client:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in .env file.")
        
        # Get real examples from database
        examples = await self.get_tradition_examples(tradition)
        
        # Build prompt
        system_prompt = self.TRADITION_PROMPTS.get(tradition, self.TRADITION_PROMPTS["Rashi"])
        mode_instruction = self.MODE_INSTRUCTIONS.get(mode, self.MODE_INSTRUCTIONS["pshat"])
        
        if examples:
            system_prompt += f"\n\nExamples of your commentary style:\n{examples}"
        
        system_prompt += f"\n\nMode: {mode_instruction}"
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""Provide commentary on this text:

Reference: {text_ref}
Text: {text}

Provide insightful commentary following your tradition's methodology."""}
                ]
            )
            
            commentary = response.choices[0].message.content
            
            # Store in Neo4j for caching
            await self.cache_commentary(text_ref, tradition, mode, commentary)
            
            return commentary
            
        except Exception as e:
            print(f"Error generating commentary: {e}")
            return f"Error generating commentary: {str(e)}"
    
    async def cache_commentary(
        self,
        text_ref: str,
        tradition: str,
        mode: str,
        commentary: str
    ):
        """Cache generated commentary in Neo4j - creates nodes if they don't exist"""
        driver = get_driver()
        
        try:
            with driver.session() as session:
                # Use MERGE to create Text node if it doesn't exist
                session.run("""
                    MERGE (t:Text {id: $text_ref})
                    ON CREATE SET t.created_at = datetime()
                    MERGE (c:AICommentary {
                        text_ref: $text_ref,
                        tradition: $tradition,
                        mode: $mode
                    })
                    SET c.content = $commentary,
                        c.generated_at = datetime(),
                        c.model = $model
                    MERGE (t)-[:HAS_AI_COMMENTARY]->(c)
                """, {
                    "text_ref": text_ref,
                    "tradition": tradition,
                    "mode": mode,
                    "commentary": commentary,
                    "model": self.model
                })
                print(f"✅ Cached commentary for {text_ref} ({tradition}/{mode})")
        except Exception as e:
            print(f"❌ Error caching commentary: {e}")
    
    async def get_cached_commentary(
        self,
        text_ref: str,
        tradition: str,
        mode: str
    ) -> Optional[str]:
        """Retrieve cached commentary from Neo4j - returns None if not found"""
        driver = get_driver()
        
        try:
            with driver.session() as session:
                # Use OPTIONAL MATCH to handle missing nodes gracefully
                result = session.run("""
                    OPTIONAL MATCH (t:Text {id: $text_ref})-[:HAS_AI_COMMENTARY]->(c:AICommentary)
                    WHERE c.tradition = $tradition AND c.mode = $mode
                    RETURN c.content as commentary
                """, {
                    "text_ref": text_ref,
                    "tradition": tradition,
                    "mode": mode
                }).single()
                
                if result and result["commentary"]:
                    print(f"✅ Found cached commentary for {text_ref}")
                    return result["commentary"]
                else:
                    print(f"ℹ️ No cached commentary for {text_ref} - will generate new")
                    return None
        except Exception as e:
            print(f"❌ Error retrieving cached commentary: {e}")
            return None

class CitationExtractor:
    """Extract halakhic citations using AI"""
    
    def __init__(self):
        self.model = "gpt-4-turbo"
    
    async def extract_citations(self, text: str) -> list:
        """Extract all Torah/Talmud citations from text"""
        
        # Check if OpenAI client is available
        if not client:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in .env file.")
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": """You are an expert in Torah literature.
Extract all citations and source references from the given text.
Include: Biblical verses, Mishnah, Gemara, Rambam, Shulchan Arukh, etc.

Return as JSON array with format:
[
    {
        "type": "Torah|Mishnah|Gemara|Rambam|etc",
        "reference": "exact reference (e.g., 'Genesis 1:1', 'Berakhot 2a')",
        "context": "brief context or quote"
    }
]
"""},
                    {"role": "user", "content": f"Extract citations from:\n\n{text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("citations", [])
            
        except Exception as e:
            print(f"Error extracting citations: {e}")
            return []

