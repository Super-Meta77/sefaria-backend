from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ManuscriptSegment(BaseModel):
    id: str
    text: str
    translation: Optional[str] = None
    footnotes: List[dict] = []
    changes: List[dict] = []

class Manuscript(BaseModel):
    id: str
    name: str
    source: str  # Vilna, Munich, Vatican, Aleppo, Leningrad, etc.
    date: Optional[str] = None
    location: Optional[str] = None
    segments: List[ManuscriptSegment]

class VersionComparisonResult(BaseModel):
    ref: str
    primary: Manuscript
    alternate: Manuscript
    differences_count: int
    significance: str  # low, medium, high

# Sample manuscript data
MANUSCRIPTS = {
    "Genesis_1_vilna": {
        "id": "Genesis_1_vilna",
        "name": "Vilna Edition",
        "source": "Vilna",
        "date": "1835",
        "location": "Vilna, Lithuania",
        "segments": [
            {
                "id": "1",
                "text": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
                "translation": "In the beginning God created the heavens and the earth",
                "footnotes": [],
                "changes": []
            },
            {
                "id": "2",
                "text": "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם",
                "translation": "And the earth was without form and void, and darkness was upon the face of the deep",
                "footnotes": [],
                "changes": []
            }
        ]
    },
    "Genesis_1_aleppo": {
        "id": "Genesis_1_aleppo",
        "name": "Aleppo Codex",
        "source": "Aleppo",
        "date": "920 CE",
        "location": "Tiberias/Aleppo",
        "segments": [
            {
                "id": "1",
                "text": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
                "translation": "In the beginning God created the heavens and the earth",
                "footnotes": [
                    {"id": "1a", "text": "Masoretic note: This word appears 5 times in Torah"}
                ],
                "changes": []
            },
            {
                "id": "2",
                "text": "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם",
                "translation": "And the earth was without form and void, and darkness was upon the face of the deep",
                "footnotes": [
                    {"id": "2a", "text": "Variant reading: Some manuscripts have slightly different vocalization"}
                ],
                "changes": [
                    {"type": "vocalization", "position": 15, "text": "Different nikud", "note": "Tiberian vs Babylonian tradition"}
                ]
            }
        ]
    }
}

@router.get("/manuscripts/{ref}", response_model=List[Manuscript])
def get_manuscript_versions(ref: str):
    """
    Get all available manuscript versions for a text reference.
    """
    # Normalize ref
    normalized_ref = ref.replace(" ", "_")
    
    # Find all manuscripts matching this ref
    results = []
    for ms_id, ms_data in MANUSCRIPTS.items():
        if normalized_ref in ms_id:
            results.append(ms_data)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No manuscripts found for {ref}")
    
    return results

@router.get("/manuscripts/compare/{ref}", response_model=VersionComparisonResult)
def compare_manuscripts(
    ref: str,
    primary: str = "vilna",
    alternate: str = "aleppo"
):
    """
    Compare two manuscript versions side-by-side with highlighted differences.
    Returns detailed segment-level comparison.
    """
    normalized_ref = ref.replace(" ", "_")
    
    # Find manuscripts
    primary_key = f"{normalized_ref}_{primary.lower()}"
    alternate_key = f"{normalized_ref}_{alternate.lower()}"
    
    if primary_key not in MANUSCRIPTS:
        raise HTTPException(status_code=404, detail=f"Primary manuscript '{primary}' not found for {ref}")
    if alternate_key not in MANUSCRIPTS:
        raise HTTPException(status_code=404, detail=f"Alternate manuscript '{alternate}' not found for {ref}")
    
    primary_ms = MANUSCRIPTS[primary_key]
    alternate_ms = MANUSCRIPTS[alternate_key]
    
    # Count differences
    diff_count = sum(len(seg.get("changes", [])) for seg in alternate_ms["segments"])
    
    # Determine significance
    if diff_count == 0:
        significance = "low"
    elif diff_count < 5:
        significance = "medium"
    else:
        significance = "high"
    
    return {
        "ref": ref,
        "primary": primary_ms,
        "alternate": alternate_ms,
        "differences_count": diff_count,
        "significance": significance
    }

@router.get("/manuscripts/sources/")
def list_manuscript_sources():
    """List all available manuscript sources."""
    sources = {}
    for ms_id, ms_data in MANUSCRIPTS.items():
        source = ms_data["source"]
        if source not in sources:
            sources[source] = {
                "name": source,
                "count": 0,
                "earliest_date": ms_data.get("date"),
                "location": ms_data.get("location")
            }
        sources[source]["count"] += 1
    
    return {"sources": list(sources.values())}

