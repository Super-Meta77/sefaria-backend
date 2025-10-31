from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

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

@router.get("/sugya/{ref}", response_model=SugyaStructure)
def get_sugya_structure(ref: str):
    """
    Get the dialectic structure of a Talmudic sugya.
    Returns a tree of questions, answers, challenges, and resolutions.
    """
    # Normalize ref (remove spaces, make consistent)
    normalized_ref = ref.replace(" ", "_")
    
    if normalized_ref in SUGYA_DATA:
        return SUGYA_DATA[normalized_ref]
    
    # Return generic structure if not found
    raise HTTPException(status_code=404, detail=f"Sugya structure not found for {ref}")

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

