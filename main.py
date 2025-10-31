from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file FIRST, before any other imports
load_dotenv()

from api import texts, connections, diffs, ai, annotations, users
from api import sugya, psak, author_map, concepts, lexical, calendar, manuscripts
from api import ai_enhanced

app = FastAPI(
    title="Sefaria Advanced Backend API",
    version="1.0",
    description="Comprehensive API for advanced Sefaria features including graph analysis, AI commentary, and more"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(texts.router, prefix="/api", tags=["texts"])
app.include_router(connections.router, prefix="/api", tags=["connections"])
app.include_router(diffs.router, prefix="/api", tags=["diffs"])
app.include_router(ai.router, prefix="/api", tags=["ai"])
app.include_router(ai_enhanced.router, prefix="/api", tags=["ai-enhanced"])
app.include_router(annotations.router, prefix="/api", tags=["annotations"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(sugya.router, prefix="/api", tags=["sugya"])
app.include_router(psak.router, prefix="/api", tags=["psak"])
app.include_router(author_map.router, prefix="/api", tags=["author-map"])
app.include_router(concepts.router, prefix="/api", tags=["concepts"])
app.include_router(lexical.router, prefix="/api", tags=["lexical"])
app.include_router(calendar.router, prefix="/api", tags=["calendar"])
app.include_router(manuscripts.router, prefix="/api", tags=["manuscripts"])

@app.get("/")
def root():
    return {
        "message": "Sefaria Advanced Backend API running!",
        "version": "1.0",
        "docs": "/docs",
        "endpoints": {
            "texts": "/api/texts/{ref}",
            "connections": "/api/connections/{node_id}",
            "diffs": "/api/diffs/",
            "ai_commentary": "/api/ai/commentary/",
            "annotations": "/api/annotations/",
            "users": "/api/users/",
            "sugya": "/api/sugya/{ref}",
            "psak": "/api/psak/{ruling_ref}",
            "author_map": "/api/author-map/",
            "concepts": "/api/concepts/",
            "lexical": "/api/lexical/{term}",
            "calendar": "/api/calendar/{date}",
            "manuscripts": "/api/manuscripts/{ref}"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "sefaria-backend"}
