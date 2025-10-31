from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Author(BaseModel):
    id: str
    name: str
    hebrew_name: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    location: Optional[str] = None
    tradition: str  # Ashkenaz, Sepharad, Mizrahi, etc.
    school: str  # rationalist, mystical, halakhic, etc.
    works: List[str] = []

class AuthorRelation(BaseModel):
    source: str
    target: str
    type: str  # teacher-student, contemporary, influenced, disputed
    strength: float

class AuthorMapData(BaseModel):
    authors: List[Author]
    relations: List[AuthorRelation]
    time_range: dict

# Sample author data
AUTHORS_DATA = {
    "rashi": {
        "id": "rashi",
        "name": "Rashi",
        "hebrew_name": "רש\"י",
        "birth_year": 1040,
        "death_year": 1105,
        "location": "Troyes, France",
        "tradition": "Ashkenaz",
        "school": "halakhic",
        "works": ["Commentary on Torah", "Commentary on Talmud"]
    },
    "rambam": {
        "id": "rambam",
        "name": "Maimonides",
        "hebrew_name": "רמב\"ם",
        "birth_year": 1138,
        "death_year": 1204,
        "location": "Cordoba, Spain / Cairo, Egypt",
        "tradition": "Sepharad",
        "school": "rationalist",
        "works": ["Mishneh Torah", "Guide for the Perplexed"]
    },
    "ramban": {
        "id": "ramban",
        "name": "Nachmanides",
        "hebrew_name": "רמב\"ן",
        "birth_year": 1194,
        "death_year": 1270,
        "location": "Girona, Spain / Jerusalem",
        "tradition": "Sepharad",
        "school": "mystical",
        "works": ["Commentary on Torah", "Torat HaAdam"]
    },
    "maharal": {
        "id": "maharal",
        "name": "Maharal of Prague",
        "hebrew_name": "מהר\"ל",
        "birth_year": 1520,
        "death_year": 1609,
        "location": "Prague, Bohemia",
        "tradition": "Ashkenaz",
        "school": "mystical",
        "works": ["Gevurot Hashem", "Netzach Yisrael"]
    }
}

RELATIONS_DATA = [
    {"source": "rashi", "target": "rambam", "type": "influenced", "strength": 0.6},
    {"source": "rambam", "target": "ramban", "type": "contemporary", "strength": 0.8},
    {"source": "ramban", "target": "maharal", "type": "influenced", "strength": 0.7},
]

@router.get("/author-map/", response_model=AuthorMapData)
def get_author_map(
    tradition: Optional[str] = None,
    school: Optional[str] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None
):
    """
    Get chronological-conceptual map of authors and their relationships.
    Filter by tradition, school, or time period.
    """
    authors = list(AUTHORS_DATA.values())
    
    # Apply filters
    if tradition:
        authors = [a for a in authors if a["tradition"] == tradition]
    if school:
        authors = [a for a in authors if a["school"] == school]
    if min_year:
        authors = [a for a in authors if a.get("birth_year", 0) >= min_year]
    if max_year:
        authors = [a for a in authors if a.get("death_year", 9999) <= max_year]
    
    # Filter relations to only include authors in filtered list
    author_ids = {a["id"] for a in authors}
    relations = [r for r in RELATIONS_DATA if r["source"] in author_ids and r["target"] in author_ids]
    
    # Calculate time range
    years = [a.get("birth_year", 0) for a in authors] + [a.get("death_year", 0) for a in authors]
    years = [y for y in years if y > 0]
    
    return {
        "authors": authors,
        "relations": relations,
        "time_range": {
            "min": min(years) if years else 0,
            "max": max(years) if years else 2024
        }
    }

@router.get("/author/{author_id}", response_model=Author)
def get_author(author_id: str):
    """Get detailed information about a specific author."""
    if author_id in AUTHORS_DATA:
        return AUTHORS_DATA[author_id]
    raise HTTPException(status_code=404, detail=f"Author {author_id} not found")

@router.get("/author/{author_id}/influences")
def get_author_influences(author_id: str):
    """Get authors who influenced or were influenced by this author."""
    if author_id not in AUTHORS_DATA:
        raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
    
    influenced_by = [r for r in RELATIONS_DATA if r["target"] == author_id]
    influenced = [r for r in RELATIONS_DATA if r["source"] == author_id]
    
    return {
        "author": author_id,
        "influenced_by": influenced_by,
        "influenced": influenced
    }

