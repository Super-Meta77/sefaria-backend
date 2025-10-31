from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict

router = APIRouter()

class SemanticNode(BaseModel):
    id: str
    term: str
    hebrew_term: str
    era: str
    meaning: str
    corpus: str
    sources: List[str] = []
    frequency: int

class SemanticLink(BaseModel):
    source: str
    target: str
    similarity: float  # cosine similarity or semantic proximity
    drift_type: str  # expansion, contraction, shift, continuity

class SemanticDriftData(BaseModel):
    term: str
    hebrew_term: str
    nodes: List[SemanticNode]
    links: List[SemanticLink]
    drift_summary: str

# Sample lexical/semantic data
LEXICAL_DATA = {
    "chesed": {
        "term": "chesed",
        "hebrew_term": "חסד",
        "nodes": [
            {
                "id": "chesed_tanakh",
                "term": "chesed",
                "hebrew_term": "חסד",
                "era": "Biblical",
                "meaning": "Covenant loyalty, steadfast love",
                "corpus": "Tanakh",
                "sources": ["Genesis 24:12", "Psalm 136"],
                "frequency": 248
            },
            {
                "id": "chesed_talmud",
                "term": "chesed",
                "hebrew_term": "חסד",
                "era": "Rabbinic",
                "meaning": "Acts of loving-kindness, charity",
                "corpus": "Talmud",
                "sources": ["Pirkei Avot 1:2", "Sukkah 49b"],
                "frequency": 156
            },
            {
                "id": "chesed_zohar",
                "term": "chesed",
                "hebrew_term": "חסד",
                "era": "Medieval Kabbalah",
                "meaning": "Divine emanation, right pillar of sefirot",
                "corpus": "Zohar",
                "sources": ["Zohar I:15a", "Zohar II:42b"],
                "frequency": 892
            },
            {
                "id": "chesed_mussar",
                "term": "chesed",
                "hebrew_term": "חסד",
                "era": "Modern Mussar",
                "meaning": "Character trait of generosity and compassion",
                "corpus": "Mussar Literature",
                "sources": ["Mesillat Yesharim Ch. 19", "Orchot Tzaddikim"],
                "frequency": 124
            }
        ],
        "links": [
            {
                "source": "chesed_tanakh",
                "target": "chesed_talmud",
                "similarity": 0.85,
                "drift_type": "expansion"
            },
            {
                "source": "chesed_talmud",
                "target": "chesed_zohar",
                "similarity": 0.65,
                "drift_type": "shift"
            },
            {
                "source": "chesed_zohar",
                "target": "chesed_mussar",
                "similarity": 0.72,
                "drift_type": "expansion"
            }
        ],
        "drift_summary": "Chesed evolves from covenant loyalty in Tanakh to practical kindness in Talmud, then to divine emanation in Kabbalah, and finally to ethical character trait in Mussar."
    },
    "din": {
        "term": "din",
        "hebrew_term": "דין",
        "nodes": [
            {
                "id": "din_tanakh",
                "term": "din",
                "hebrew_term": "דין",
                "era": "Biblical",
                "meaning": "Judgment, justice",
                "corpus": "Tanakh",
                "sources": ["Genesis 18:25", "Deuteronomy 1:17"],
                "frequency": 142
            },
            {
                "id": "din_talmud",
                "term": "din",
                "hebrew_term": "דין",
                "era": "Rabbinic",
                "meaning": "Legal case, law, judgment",
                "corpus": "Talmud",
                "sources": ["Bava Kamma 46a", "Sanhedrin 6a"],
                "frequency": 1456
            },
            {
                "id": "din_kabbalah",
                "term": "din",
                "hebrew_term": "דין",
                "era": "Medieval Kabbalah",
                "meaning": "Divine attribute of strict judgment, left pillar",
                "corpus": "Kabbalistic texts",
                "sources": ["Zohar", "Etz Chaim"],
                "frequency": 634
            }
        ],
        "links": [
            {
                "source": "din_tanakh",
                "target": "din_talmud",
                "similarity": 0.90,
                "drift_type": "expansion"
            },
            {
                "source": "din_talmud",
                "target": "din_kabbalah",
                "similarity": 0.58,
                "drift_type": "shift"
            }
        ],
        "drift_summary": "Din shifts from judicial judgment in Tanakh to legal procedural meaning in Talmud, then to cosmic attribute in Kabbalah."
    }
}

@router.get("/lexical/{term}", response_model=SemanticDriftData)
def get_semantic_drift(term: str):
    """
    Track how a Hebrew/Aramaic term changes meaning across time and genre.
    Returns nodes representing the term in different corpora and links showing semantic drift.
    """
    if term in LEXICAL_DATA:
        return LEXICAL_DATA[term]
    
    raise HTTPException(status_code=404, detail=f"Lexical data for '{term}' not found")

@router.get("/lexical/")
def list_terms(corpus: Optional[str] = None):
    """List all available terms in the lexical hypergraph."""
    terms = []
    for term_id, data in LEXICAL_DATA.items():
        if corpus:
            # Filter nodes by corpus
            nodes = [n for n in data["nodes"] if n["corpus"].lower() == corpus.lower()]
            if nodes:
                terms.append({
                    "term": data["term"],
                    "hebrew_term": data["hebrew_term"],
                    "corpora": list(set([n["corpus"] for n in nodes]))
                })
        else:
            terms.append({
                "term": data["term"],
                "hebrew_term": data["hebrew_term"],
                "corpora": list(set([n["corpus"] for n in data["nodes"]]))
            })
    
    return {"terms": terms}

@router.get("/lexical/{term}/compare")
def compare_usage(term: str, corpus1: str, corpus2: str):
    """
    Compare how a term is used in two different corpora.
    Returns side-by-side semantic analysis.
    """
    if term not in LEXICAL_DATA:
        raise HTTPException(status_code=404, detail=f"Term '{term}' not found")
    
    data = LEXICAL_DATA[term]
    node1 = next((n for n in data["nodes"] if n["corpus"].lower() == corpus1.lower()), None)
    node2 = next((n for n in data["nodes"] if n["corpus"].lower() == corpus2.lower()), None)
    
    if not node1 or not node2:
        raise HTTPException(status_code=404, detail=f"Comparison data not available for specified corpora")
    
    # Find link between them
    link = next((l for l in data["links"] if 
                 (l["source"] == node1["id"] and l["target"] == node2["id"]) or
                 (l["source"] == node2["id"] and l["target"] == node1["id"])), None)
    
    return {
        "term": term,
        "corpus1": node1,
        "corpus2": node2,
        "relationship": link,
        "analysis": f"The term '{term}' shows {link['drift_type'] if link else 'unknown'} semantic drift between {corpus1} and {corpus2}"
    }

