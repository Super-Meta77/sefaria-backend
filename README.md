# Sefaria Advanced Backend API

Comprehensive FastAPI backend for the advanced Sefaria platform, implementing all 10 core engines and features from the project requirements.

## Features Implemented

### 1. **Dynamic Intertextual Graph Engine** ✅
- **Endpoint**: `/api/connections/{node_id}`
- **Features**: 
  - Neo4j-powered graph queries
  - Advanced filtering (genre, author, era, connection type)
  - Multi-hop graph traversal
  - Graph visualization data export

### 2. **Textual Topology Engine (Versional Criticism)** ✅
- **Endpoints**: 
  - `/api/manuscripts/{ref}` - Get all manuscript versions
  - `/api/manuscripts/compare/{ref}` - Compare two versions side-by-side
- **Features**:
  - Multiple manuscript sources (Vilna, Aleppo, Munich, Vatican, etc.)
  - Segment-level diffs with highlighting
  - Footnotes and variant readings

### 3. **Dialectic Mapping & Sugya Structure** ✅
- **Endpoints**:
  - `/api/sugya/{ref}` - Get sugya logic tree
  - `/api/sugya/{ref}/flow` - Get flow visualization data
- **Features**:
  - Hierarchical Q&A structure
  - Question, answer, challenge (kasha), resolution (terutz) mapping
  - Teiku (unresolved) tracking

### 4. **Psak Lineage Tracer** ✅
- **Endpoints**:
  - `/api/psak/{ruling_ref}` - Trace halakhic ruling lineage
  - `/api/psak/search/` - Search rulings
- **Features**:
  - Torah → Mishnah → Gemara → Rishonim → Acharonim chains
  - Timeline visualization data
  - Source attribution

### 5. **AI-Assisted Commentarial Layering** ✅
- **Endpoints**:
  - `/api/ai/commentary/{text_ref}` (GET)
  - `/api/ai/commentary/` (POST)
- **Features**:
  - Tradition selection (Rashi, Ramban, Maharal, etc.)
  - Interpretive modes (pshat, halakhah, mystical)
  - Ready for LLM integration

### 6. **Chronological-Conceptual Author Map** ✅
- **Endpoints**:
  - `/api/author-map/` - Get author network with filters
  - `/api/author/{author_id}` - Get author details
  - `/api/author/{author_id}/influences` - Get influence relationships
- **Features**:
  - Geographic and chronological data
  - School/tradition clustering
  - Influence relationships

### 7. **Queryable Conceptual Index** ✅
- **Endpoints**:
  - `/api/concepts/` - List all concepts
  - `/api/concepts/{concept_id}` - Get concept details
  - `/api/concepts/search/` - Search concepts
  - `/api/concepts/{concept_id}/by-tradition` - Tradition-based clustering
- **Features**:
  - Multi-tradition anthology
  - Hashkafic lens filtering (Maimonidean, Kabbalistic, Hasidic, etc.)
  - Cross-reference excerpts

### 8. **Lexical Hypergraph for Semantic Drift** ✅
- **Endpoints**:
  - `/api/lexical/{term}` - Track semantic drift
  - `/api/lexical/` - List terms
  - `/api/lexical/{term}/compare` - Compare usage across corpora
- **Features**:
  - Track meaning evolution across time/genre
  - Corpus-specific word embeddings
  - Semantic similarity scoring

### 9. **Collaborative Annotation Platform** ✅
- **Endpoints**:
  - `/api/annotations/{text_ref}` - Get annotations for text
  - `/api/annotations/user/{username}` - Get user's annotations
  - `/api/annotations/` (POST) - Add annotation
  - `/api/annotations/{idx}` (PUT) - Edit annotation
  - `/api/annotations/{idx}` (DELETE) - Delete annotation
- **Features**:
  - Multi-layer annotation system
  - User attribution
  - Type categorization

### 10. **Liturgical & Calendar Sync Engine** ✅
- **Endpoints**:
  - `/api/calendar/{date}` - Get learning schedule for date
  - `/api/calendar/today/` - Get today's schedule
  - `/api/calendar/range/` - Get date range
  - `/api/calendar/cycle/{cycle_type}` - Get cycle info
- **Features**:
  - Daf Yomi, Parsha, Haftara
  - Daily Rambam, holidays, fast days
  - Hebrew calendar integration

## Additional Features

### Text Retrieval ✅
- **Endpoint**: `/api/texts/{ref}`
- Fetches from Sefaria public API (swappable with local DB)

### Text Comparison/Diffs ✅
- **Endpoint**: `/api/diffs/`
- Word-level diff algorithm

### User Management & Authentication ✅
- **Endpoints**:
  - `/api/users/register` - Register new user
  - `/api/users/login` - User login
  - `/api/users/{username}` - Get user profile
  - `/api/users/` - List users
- Password hashing with bcrypt
- Ready for JWT token authentication

## Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Edit `database.py` to configure your Neo4j connection:

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"
```

## Running the Server

```bash
# Development mode with auto-reload
uvicorn backend.main:app --reload

# Production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root Endpoint Info**: http://localhost:8000/

## Frontend Integration

CORS is configured for:
- `http://localhost:3000`
- `http://localhost:3001`

Add additional origins in `main.py` as needed.

## Project Structure

```
backend/
├── main.py              # FastAPI app entry, middleware, router registration
├── database.py          # Neo4j connection setup
├── models.py            # Pydantic models for request/response
├── requirements.txt     # Python dependencies
├── api/
│   ├── __init__.py
│   ├── texts.py         # Text retrieval
│   ├── connections.py   # Intertextual graph
│   ├── diffs.py         # Text comparison
│   ├── ai.py            # AI commentary
│   ├── annotations.py   # Annotation management
│   ├── users.py         # User auth
│   ├── sugya.py         # Dialectic mapping
│   ├── psak.py          # Psak lineage
│   ├── author_map.py    # Author relationships
│   ├── concepts.py      # Concept index
│   ├── lexical.py       # Semantic drift
│   ├── calendar.py      # Calendar integration
│   └── manuscripts.py   # Version comparison
└── README.md
```

## Next Steps

1. **Data Integration**: Connect to your production databases (Neo4j, text corpus, manuscripts)
2. **AI/NLP**: Wire up `/api/ai/commentary/` to your LLM inference endpoint
3. **JWT Auth**: Implement token-based authentication for secure routes
4. **Testing**: Add pytest test suites for all endpoints
5. **Deployment**: Dockerize and deploy to production environment
6. **Monitoring**: Add logging, metrics, and error tracking

## API Examples

### Get Text
```bash
curl http://localhost:8000/api/texts/Genesis.1.1
```

### Get Connections with Filters
```bash
curl "http://localhost:8000/api/connections/Genesis_1_1?genre=halakhic&era=Rishonic"
```

### Search Concepts
```bash
curl "http://localhost:8000/api/concepts/search/?query=chesed&tradition=Hasidic"
```

### Get Today's Learning
```bash
curl http://localhost:8000/api/calendar/today/
```

### Compare Manuscripts
```bash
curl "http://localhost:8000/api/manuscripts/compare/Genesis_1?primary=vilna&alternate=aleppo"
```

## License

[Add your license here]

## Contributors

[Add contributors]

