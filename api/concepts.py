from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ConceptReference(BaseModel):
    ref: str
    text: str
    author: Optional[str] = None
    tradition: str
    excerpt: str

class Concept(BaseModel):
    id: str
    name: str
    hebrew_name: str
    description: str
    category: str  # theological, philosophical, ethical, halakhic
    references: List[ConceptReference] = []

class ConceptSearchResult(BaseModel):
    concept: Concept
    relevance: float

# Sample concept data
CONCEPTS_DATA = {
    "chesed": {
        "id": "chesed",
        "name": "Chesed",
        "hebrew_name": "חסד",
        "description": "Loving-kindness, grace, benevolence",
        "category": "theological",
        "references": [
            {
                "ref": "Genesis 24:12",
                "text": "עֲשֵׂה־חֶסֶד עִם־אֲדֹנִי אַבְרָהָם",
                "tradition": "Biblical",
                "excerpt": "Show kindness to my master Abraham"
            },
            {
                "ref": "Pirkei Avot 1:2",
                "text": "עַל שְׁלשָׁה דְבָרִים הָעוֹלָם עוֹמֵד, עַל הַתּוֹרָה וְעַל הָעֲבוֹדָה וְעַל גְּמִילוּת חֲסָדִים",
                "author": "Shimon HaTzaddik",
                "tradition": "Rabbinic",
                "excerpt": "The world stands on three things: Torah, service, and acts of kindness"
            },
            {
                "ref": "Tanya, Chapter 15",
                "text": "Chesed represents the right hand of divine emanation",
                "author": "Rabbi Schneur Zalman of Liadi",
                "tradition": "Hasidic",
                "excerpt": "Kabbalistic understanding of divine attributes"
            }
        ]
    },
    "emunah": {
        "id": "emunah",
        "name": "Emunah",
        "hebrew_name": "אמונה",
        "description": "Faith, belief, trust in God",
        "category": "theological",
        "references": [
            {
                "ref": "Habakkuk 2:4",
                "text": "וְצַדִּיק בֶּאֱמוּנָתוֹ יִחְיֶה",
                "tradition": "Biblical",
                "excerpt": "The righteous shall live by his faith"
            },
            {
                "ref": "Rambam, Mishneh Torah, Yesodei HaTorah 1:1",
                "text": "The foundation of foundations and pillar of wisdom is to know that there is a First Being",
                "author": "Maimonides",
                "tradition": "Rationalist",
                "excerpt": "Rational approach to faith"
            }
        ]
    },
    "teshuvah": {
        "id": "teshuvah",
        "name": "Teshuvah",
        "hebrew_name": "תשובה",
        "description": "Repentance, return to God",
        "category": "ethical",
        "references": [
            {
                "ref": "Deuteronomy 30:2",
                "text": "וְשַׁבְתָּ עַד־יְהוָה אֱלֹהֶיךָ",
                "tradition": "Biblical",
                "excerpt": "And you shall return to the Lord your God"
            },
            {
                "ref": "Rambam, Hilchot Teshuvah 2:1",
                "text": "What is complete teshuvah? When one has the opportunity to repeat a sin but refrains",
                "author": "Maimonides",
                "tradition": "Halakhic",
                "excerpt": "Definition of complete repentance"
            }
        ]
    }
}

@router.get("/concepts/", response_model=List[Concept])
def list_concepts(category: Optional[str] = None):
    """List all available concepts, optionally filtered by category."""
    concepts = list(CONCEPTS_DATA.values())
    if category:
        concepts = [c for c in concepts if c["category"] == category]
    return concepts

@router.get("/concepts/{concept_id}", response_model=Concept)
def get_concept(concept_id: str):
    """Get detailed information about a specific concept."""
    if concept_id in CONCEPTS_DATA:
        return CONCEPTS_DATA[concept_id]
    raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")

@router.get("/concepts/search/", response_model=List[ConceptSearchResult])
def search_concepts(
    query: str,
    tradition: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Search for Torah concepts and return references across traditions.
    Filter by tradition (Biblical, Rabbinic, Kabbalistic, Hasidic, Rationalist, etc.)
    or category (theological, philosophical, ethical, halakhic).
    """
    results = []
    
    for concept_id, concept_data in CONCEPTS_DATA.items():
        # Simple text matching
        relevance = 0.0
        if query.lower() in concept_data["name"].lower():
            relevance += 1.0
        if query.lower() in concept_data["hebrew_name"]:
            relevance += 1.0
        if query.lower() in concept_data["description"].lower():
            relevance += 0.5
        
        if relevance > 0:
            # Filter references by tradition if specified
            refs = concept_data["references"]
            if tradition:
                refs = [r for r in refs if r["tradition"].lower() == tradition.lower()]
            
            # Apply category filter
            if category and concept_data["category"] != category:
                continue
            
            filtered_concept = {**concept_data, "references": refs}
            results.append({
                "concept": filtered_concept,
                "relevance": relevance
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results

@router.get("/concepts/{concept_id}/by-tradition")
def get_concept_by_tradition(concept_id: str):
    """
    Get concept references grouped by tradition/hashkafic lens.
    Returns clustered view (Maimonidean, Kabbalistic, Hasidic, etc.)
    """
    if concept_id not in CONCEPTS_DATA:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    
    concept = CONCEPTS_DATA[concept_id]
    
    # Group references by tradition
    by_tradition = {}
    for ref in concept["references"]:
        trad = ref["tradition"]
        if trad not in by_tradition:
            by_tradition[trad] = []
        by_tradition[trad].append(ref)
    
    return {
        "concept": concept["name"],
        "hebrew_name": concept["hebrew_name"],
        "by_tradition": by_tradition
    }

