# AI Implementation Plan for Advanced Sefaria Engines

## Current State Analysis

### ✅ What We Have (From Sefaria Neo4j DB)
- **727,309 nodes**: Author, Category, Concept, Event, Text, Tradition, Version, Work
- **1,258,688 relationships**: CITES, COMMENTARY_ON, EXPLICIT, BELONGS_TO, MEMBER_OF, etc.
- **Structural data**: Text hierarchies, authorship, citations

### ❌ What We Need to Build
- **Semantic embeddings** for texts (vector representations)
- **AI-generated commentary** system
- **NLP processing** for Hebrew/Aramaic texts
- **Semantic drift tracking** across corpora
- **Conceptual indexing** with embeddings
- **Dialectic structure extraction** from sugyot
- **Psak lineage inference** using ML
- **Lexical analysis** with word embeddings

---

## Implementation Roadmap

### Phase 1: AI Infrastructure Setup (Weeks 1-2)

#### 1.1 Add Vector Support to Neo4j
```cypher
// Enable vector index on Text nodes
CREATE VECTOR INDEX text_embeddings IF NOT EXISTS
FOR (t:Text)
ON t.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

// Enable vector index on Concept nodes
CREATE VECTOR INDEX concept_embeddings IF NOT EXISTS
FOR (c:Concept)
ON c.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};
```

#### 1.2 Set Up AI/ML Services
- **OpenAI API** for embeddings and GPT-4 commentary
- **Hugging Face** for Hebrew NLP models
- **Local LLM** (Optional: Llama 2/3 for cost savings)
- **Redis** for caching AI responses

#### 1.3 Update Backend Dependencies
```txt
# Add to requirements.txt
openai>=1.0.0
tiktoken>=0.5.0
sentence-transformers>=2.2.0
transformers>=4.35.0
torch>=2.0.0
redis>=5.0.0
langchain>=0.1.0
chromadb>=0.4.0  # For local vector storage
```

---

### Phase 2: Text Embedding Pipeline (Weeks 3-4)

#### 2.1 Embed All Texts
```python
# backend/ai/embeddings.py

from openai import OpenAI
from neo4j import GraphDatabase
import tiktoken

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def embed_text_node(text_id: str, content: str):
    """Generate embedding for a text and store in Neo4j"""
    
    # Generate embedding using OpenAI
    response = client.embeddings.create(
        model="text-embedding-3-large",  # 1536 dimensions
        input=content[:8000]  # Limit token size
    )
    
    embedding = response.data[0].embedding
    
    # Store in Neo4j
    driver = get_driver()
    with driver.session() as session:
        session.run("""
            MATCH (t:Text {`<id>`: $text_id})
            SET t.embedding = $embedding,
                t.embedding_model = 'text-embedding-3-large',
                t.embedded_at = datetime()
        """, {"text_id": text_id, "embedding": embedding})
    
    return embedding

async def batch_embed_all_texts():
    """Embed all Text nodes in the database"""
    driver = get_driver()
    
    with driver.session() as session:
        # Get all texts without embeddings
        result = session.run("""
            MATCH (t:Text)
            WHERE t.embedding IS NULL
            RETURN t.`<id>` as id, 
                   coalesce(t.content_he, t.content_en) as content
            LIMIT 1000
        """)
        
        for record in result:
            await embed_text_node(record["id"], record["content"])
```

#### 2.2 Semantic Search Endpoint
```python
# backend/api/semantic_search.py

@router.post("/semantic-search/")
async def semantic_search(query: str, limit: int = 10):
    """Find texts semantically similar to query"""
    
    # Generate query embedding
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=query
    )
    query_embedding = response.data[0].embedding
    
    # Search Neo4j vector index
    driver = get_driver()
    with driver.session() as session:
        results = session.run("""
            CALL db.index.vector.queryNodes(
                'text_embeddings', 
                $limit, 
                $query_embedding
            )
            YIELD node, score
            RETURN node.`<id>` as id,
                   node.id as text_ref,
                   coalesce(node.content_he, node.content_en) as content,
                   score
        """, {"limit": limit, "query_embedding": query_embedding})
        
        return [dict(record) for record in results]
```

---

### Phase 3: AI Commentary Engine (Weeks 5-6)

#### 3.1 Fine-Tuned Commentary Models
```python
# backend/ai/commentary.py

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class CommentaryGenerator:
    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.3
        )
    
    async def generate_commentary(
        self,
        text: str,
        tradition: str = "Rashi",
        mode: str = "pshat"
    ):
        """Generate commentary in style of specified tradition"""
        
        # Load tradition-specific examples from database
        examples = await self.get_tradition_examples(tradition)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a Torah scholar generating commentary 
            in the style of {tradition}. Mode: {mode}.
            
            Examples of {tradition}'s style:
            {examples}
            
            Generate insightful commentary following this tradition's 
            methodology and interpretive approach."""),
            ("user", f"Text: {text}\n\nProvide commentary:")
        ])
        
        chain = prompt | self.model
        response = await chain.ainvoke({})
        
        return response.content
    
    async def get_tradition_examples(self, tradition: str):
        """Fetch real commentary examples from Neo4j"""
        driver = get_driver()
        
        with driver.session() as session:
            result = session.run("""
                MATCH (a:Author {name: $tradition})-[:WRITTEN_BY]-(c:Text)
                WHERE c.category = 'Commentary'
                RETURN c.content_he as content
                LIMIT 5
            """, {"tradition": tradition})
            
            examples = [record["content"] for record in result]
            return "\n\n".join(examples)
```

#### 3.2 Update AI API Endpoint
```python
# backend/api/ai.py - Replace stub with real implementation

@router.post("/ai/commentary/", response_model=AICommentary)
async def ai_commentary_post(payload: AICommentaryRequest):
    """Generate AI commentary with actual LLM"""
    
    generator = CommentaryGenerator()
    
    # Get original text
    text = await get_text_content(payload.text_ref)
    
    # Generate commentary
    generated = await generator.generate_commentary(
        text=text,
        tradition=payload.tradition,
        mode=payload.mode
    )
    
    # Cache the result
    await cache_commentary(payload.text_ref, payload.tradition, generated)
    
    return AICommentary(
        text_ref=payload.text_ref,
        tradition=payload.tradition,
        mode=payload.mode,
        generated=generated
    )
```

---

### Phase 4: Semantic Drift & Lexical Analysis (Weeks 7-8)

#### 4.1 Build Word Embeddings Per Corpus
```python
# backend/ai/lexical_analysis.py

from transformers import AutoTokenizer, AutoModel
import torch

class HebrewWordEmbeddings:
    def __init__(self):
        # Use AlephBERT for Hebrew
        self.tokenizer = AutoTokenizer.from_pretrained("onlplab/alephbert-base")
        self.model = AutoModel.from_pretrained("onlplab/alephbert-base")
    
    async def track_semantic_drift(self, term: str):
        """Track how a term's meaning evolves across corpora"""
        
        corpora = ["Tanakh", "Talmud", "Zohar", "Mussar"]
        embeddings_by_corpus = {}
        
        for corpus in corpora:
            # Get contexts where term appears in this corpus
            contexts = await self.get_term_contexts(term, corpus)
            
            # Generate contextual embeddings
            embeddings = []
            for context in contexts:
                inputs = self.tokenizer(context, return_tensors="pt")
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # Get embedding for the term
                embedding = outputs.last_hidden_state.mean(dim=1)
                embeddings.append(embedding)
            
            # Average embeddings for this corpus
            corpus_embedding = torch.stack(embeddings).mean(dim=0)
            embeddings_by_corpus[corpus] = corpus_embedding
        
        # Calculate drift between corpora
        drift_analysis = self.calculate_drift(embeddings_by_corpus)
        
        return drift_analysis
    
    async def get_term_contexts(self, term: str, corpus: str):
        """Get text contexts containing term from specific corpus"""
        driver = get_driver()
        
        with driver.session() as session:
            result = session.run("""
                MATCH (t:Text)-[:BELONGS_TO]->(c:Category {name: $corpus})
                WHERE t.content_he CONTAINS $term
                RETURN t.content_he as context
                LIMIT 100
            """, {"term": term, "corpus": corpus})
            
            return [record["context"] for record in result]
```

#### 4.2 Store Semantic Drift in Neo4j
```cypher
// Create SemanticEvolution nodes
CREATE (se:SemanticEvolution {
    term: 'chesed',
    corpus_from: 'Tanakh',
    corpus_to: 'Talmud',
    drift_score: 0.35,
    drift_type: 'expansion',
    analysis: 'Term broadens from covenant loyalty to general kindness'
})
```

---

### Phase 5: Dialectic Mapping with NLP (Weeks 9-10)

#### 5.1 Extract Sugya Structure Using AI
```python
# backend/ai/sugya_parser.py

class SugyaParser:
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-4-turbo")
    
    async def parse_sugya(self, sugya_text: str):
        """Parse Talmudic sugya into dialectic structure"""
        
        prompt = f"""Analyze this Talmudic sugya and extract its dialectic structure.
        Identify:
        1. Questions (she'elot)
        2. Answers (teshuvot)
        3. Challenges (kushyot)
        4. Resolutions (terutzim)
        5. Unresolved issues (teiku)
        6. Logic connections (kal vachomer, gezeirah shavah, etc.)
        
        Sugya text:
        {sugya_text}
        
        Return as JSON with nested structure showing the flow of argument.
        """
        
        response = await self.model.ainvoke(prompt)
        sugya_structure = json.loads(response.content)
        
        # Store in Neo4j
        await self.store_sugya_structure(sugya_structure)
        
        return sugya_structure
    
    async def store_sugya_structure(self, structure: dict):
        """Store parsed sugya structure in Neo4j"""
        driver = get_driver()
        
        with driver.session() as session:
            # Create nodes for each dialectic element
            session.run("""
                CREATE (q:Question {
                    text: $text,
                    sugya_ref: $ref
                })
            """, structure["question"])
            
            # Link with LEADS_TO relationships
            # ... recursive structure creation
```

---

### Phase 6: Psak Lineage with ML Inference (Weeks 11-12)

#### 6.1 Citation Extraction & Chain Building
```python
# backend/ai/psak_tracer.py

class PsakLineageBuilder:
    async def build_lineage_chain(self, ruling_ref: str):
        """Use AI to trace halakhic ruling sources"""
        
        # Get the ruling text
        ruling_text = await self.get_ruling_text(ruling_ref)
        
        # Use AI to extract citations
        citations = await self.extract_citations(ruling_text)
        
        # Build chain recursively
        chain = []
        for citation in citations:
            # Find in Neo4j
            source = await self.find_source(citation)
            if source:
                chain.append(source)
                
                # Recurse to find earlier sources
                earlier = await self.build_lineage_chain(source.ref)
                chain.extend(earlier)
        
        # Store as DERIVES_FROM relationships in Neo4j
        await self.store_lineage_chain(ruling_ref, chain)
        
        return chain
    
    async def extract_citations(self, text: str):
        """Use GPT to extract halakhic citations"""
        prompt = f"""Extract all halakhic source citations from this text.
        Include: Torah verses, Mishnah, Gemara, Rambam, Tur, etc.
        
        Text: {text}
        
        Return as JSON list of citations with type and reference.
        """
        
        response = await self.model.ainvoke(prompt)
        return json.loads(response.content)
```

---

### Phase 7: Conceptual Index with Embeddings (Weeks 13-14)

#### 7.1 Build Concept Graph
```python
# backend/ai/concept_indexer.py

class ConceptIndexer:
    async def index_concept(self, concept_name: str):
        """Find and index all references to a concept"""
        
        # Generate concept embedding
        concept_embedding = await self.embed_concept(concept_name)
        
        # Find semantically similar texts
        similar_texts = await self.semantic_search(concept_embedding)
        
        # Create DISCUSSES_CONCEPT relationships
        driver = get_driver()
        with driver.session() as session:
            for text in similar_texts:
                session.run("""
                    MATCH (t:Text {`<id>`: $text_id})
                    MATCH (c:Concept {name: $concept})
                    MERGE (t)-[r:DISCUSSES_CONCEPT]->(c)
                    SET r.relevance_score = $score,
                        r.context = $context
                """, {
                    "text_id": text.id,
                    "concept": concept_name,
                    "score": text.score,
                    "context": text.excerpt
                })
```

---

## Technology Stack

### AI/ML Services
- **OpenAI GPT-4**: Commentary generation, structure parsing
- **OpenAI Embeddings**: text-embedding-3-large (1536d)
- **Hugging Face Transformers**: AlephBERT for Hebrew NLP
- **LangChain**: Orchestration and prompt management
- **Redis**: Caching AI responses

### Vector Storage
- **Neo4j Vector Indexes**: Primary vector storage
- **ChromaDB**: Secondary/local vector database
- **Pinecone** (Optional): Scalable vector search

### NLP Models
- **AlephBERT**: Hebrew language understanding
- **mT5**: Multilingual text generation
- **Hebrew NER models**: Entity extraction

---

## Implementation Priority

### Must Have (Core AI Features)
1. ✅ Text embeddings for semantic search
2. ✅ AI commentary generation
3. ✅ Citation extraction and lineage building
4. ✅ Concept indexing with vectors

### Should Have (Enhanced Features)
5. ⏳ Semantic drift analysis
6. ⏳ Dialectic structure parsing
7. ⏳ Multi-tradition commentary styles
8. ⏳ Hebrew NLP pipelines

### Nice to Have (Advanced Features)
9. ⏳ Fine-tuned models on Sefaria corpus
10. ⏳ Real-time collaborative learning
11. ⏳ Automated source attribution
12. ⏳ Multi-modal (audio/text) integration

---

## Cost Estimates

### OpenAI API Costs (Monthly)
- **Embeddings**: ~$50/month (727K texts × $0.00013/1K tokens)
- **GPT-4 Commentary**: ~$200/month (moderate usage)
- **Total**: ~$250-500/month

### Infrastructure
- **Neo4j Cloud**: $65-200/month (depending on instance)
- **Redis Cache**: $10-30/month
- **Total**: ~$75-230/month

### One-Time Costs
- **Initial embedding generation**: ~$100
- **Model fine-tuning** (optional): $500-2000

**Total Monthly**: ~$325-730 for full AI features

---

## Next Steps

1. **Set up OpenAI API** and add key to `.env`
2. **Create vector indexes** in Neo4j
3. **Implement embedding pipeline** (Phase 2)
4. **Build AI commentary** (Phase 3)
5. **Integrate with frontend**

See `AI_IMPLEMENTATION_GUIDE.md` for detailed code examples.

