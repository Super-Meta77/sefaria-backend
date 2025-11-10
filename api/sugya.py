from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from .sugya_manager import get_sugya_manager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ai.sugya_extractor import get_sugya_extractor

router = APIRouter()

class SugyaNode(BaseModel):
    id: str
    type: str  # question, answer, kasha, terutz, teiku, dispute, resolution
    label: str
    sugyaLocation: str
    children: List['SugyaNode'] = []

class SugyaStructure(BaseModel):
    ref: str
    title: str
    root: SugyaNode
    summary: str

# Sample sugya data structure
SUGYA_DATA = {
    "Berakhot_2a": {
        "ref": "Berakhot 2a",
        "title": "Time for Evening Shema",
        "summary": "This sugya explores when the evening Shema should be recited, presenting various opinions and their reasoning.",
        "root": {
            "id": "q1",
            "type": "question",
            "label": "When do we recite the evening Shema?",
            "sugyaLocation": "2a:1",
            "children": [
                {
                    "id": "a1",
                    "type": "answer",
                    "label": "From when priests eat terumah (when stars appear)",
                    "sugyaLocation": "2a:2",
                    "children": [
                        {
                            "id": "k1",
                            "type": "kasha",
                            "label": "When exactly do stars appear?",
                            "sugyaLocation": "2a:3",
                            "children": [
                                {
                                    "id": "dispute1",
                                    "type": "dispute",
                                    "label": "R. Eliezer: Until end of first watch; Sages: Until midnight",
                                    "sugyaLocation": "2a:4",
                                    "children": [
                                        {
                                            "id": "t1",
                                            "type": "terutz",
                                            "label": "Different interpretations of 'evening' - halakhic vs. practical time",
                                            "sugyaLocation": "2a:5",
                                            "children": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
}

@router.get("/sugya/list/available")
def list_available_sugyot():
    """
    Get list of all available sugya references from the Neo4j database.
    Returns array of sugya references with titles.
    """
    try:
        manager = get_sugya_manager()
        sugyot = manager.list_all_sugyot()
        return {"sugyot": sugyot, "total": len(sugyot)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/sugya/{ref}", response_model=SugyaStructure)
def get_sugya_structure(ref: str):
    """
    Get the dialectic structure of a Talmudic sugya from the Neo4j database.
    Returns a tree of questions, answers, challenges, and resolutions.
    """
    try:
        manager = get_sugya_manager()
        structure = manager.get_sugya_structure(ref)
        
        if structure:
            return structure
        
        # Return generic structure if not found
        raise HTTPException(status_code=404, detail=f"Sugya not found for {ref}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/sugya/{ref}/flow", response_model=List[dict])
def get_sugya_flow(ref: str):
    """
    Get a simplified flow representation of the sugya for visualization.
    Returns nodes with positions for graph layout.
    """
    normalized_ref = ref.replace(" ", "_")
    
    # Return flow data for visualization
    flow = [
        {"id": 1, "type": "question", "text": "When do we recite evening Shema?", "position": {"x": 0, "y": 0}},
        {"id": 2, "type": "answer", "text": "From when priests eat terumah", "position": {"x": 1, "y": 0}},
        {"id": 3, "type": "kasha", "text": "But when exactly is that?", "position": {"x": 2, "y": 0}},
        {"id": 4, "type": "dispute", "text": "R. Eliezer vs Sages dispute", "position": {"x": 3, "y": 0}},
        {"id": 5, "type": "terutz", "text": "Different interpretations of timing", "position": {"x": 4, "y": 0}},
        {"id": 6, "type": "resolution", "text": "Practical halakha follows Sages", "position": {"x": 5, "y": 0}},
    ]
    
    return flow

# Enable forward references for recursive model
SugyaNode.model_rebuild()

# ============================================================================
# AI-Powered Extraction Endpoints
# ============================================================================

@router.post("/sugya/extract/{tractate}")
def extract_sugyot_from_tractate(
    tractate: str,
    background_tasks: BackgroundTasks,
    start_page: str = "2a",
    limit: int = 50
):
    """
    Trigger AI-powered extraction of sugyot from a Talmudic tractate.
    
    This endpoint uses GPT-4 to:
    - Analyze Talmudic texts
    - Identify sugya boundaries
    - Extract dialectic structure
    - Save results to database
    
    Args:
        tractate: Name of tractate (e.g., "Berakhot")
        start_page: Starting page (e.g., "2a")
        limit: Maximum number of texts to analyze
    
    Returns:
        Job status and initial information
    """
    try:
        extractor = get_sugya_extractor()
        
        # Run extraction in background
        background_tasks.add_task(
            extractor.extract_and_save_all,
            tractate=tractate,
            start_page=start_page,
            limit=limit
        )
        
        return {
            "status": "started",
            "message": f"AI extraction started for {tractate} from {start_page}",
            "tractate": tractate,
            "start_page": start_page,
            "limit": limit,
            "note": "This process may take several minutes. Check logs for progress."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

@router.post("/sugya/extract-sync/{tractate}")
def extract_sugyot_sync(
    tractate: str,
    start_page: str = "2a",
    limit: int = 20
):
    """
    Synchronous version of sugya extraction (waits for completion).
    Use for smaller extractions.
    
    Returns:
        Extraction statistics
    """
    try:
        extractor = get_sugya_extractor()
        stats = extractor.extract_and_save_all(
            tractate=tractate,
            start_page=start_page,
            limit=limit
        )
        
        return {
            "status": "completed",
            "stats": stats,
            "message": f"Extracted {stats['saved']} sugyot from {tractate}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

@router.post("/sugya/extract-all")
def extract_all_sugyot(
    background_tasks: BackgroundTasks,
    limit_per_tractate: int = 100
):
    """
    Trigger AI-powered extraction from ALL tractates in the database.
    
    This endpoint automatically:
    - Discovers all Talmudic tractates in Neo4j
    - Extracts sugyot from each tractate
    - Saves all results to database
    
    Args:
        limit_per_tractate: Maximum texts to analyze per tractate
    
    Returns:
        Job status
    """
    try:
        extractor = get_sugya_extractor()
        
        # Run in background
        background_tasks.add_task(
            extractor.extract_all_sugyot,
            limit_per_tractate=limit_per_tractate
        )
        
        return {
            "status": "started",
            "message": "AI extraction started for ALL tractates",
            "limit_per_tractate": limit_per_tractate,
            "note": "This process may take several minutes to hours. Check logs for progress."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

@router.post("/sugya/extract-all-sync")
def extract_all_sugyot_sync(limit_per_tractate: int = 50):
    """
    Synchronous version of extract-all (waits for completion).
    Use for smaller limits.
    
    WARNING: This may take a long time!
    
    Returns:
        Extraction statistics for all tractates
    """
    try:
        extractor = get_sugya_extractor()
        stats = extractor.extract_all_sugyot(
            limit_per_tractate=limit_per_tractate
        )
        
        return {
            "status": "completed",
            "stats": stats,
            "message": f"Extracted from {stats['tractates_processed']} tractates, saved {stats['total_saved']} sugyot"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

