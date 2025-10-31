from fastapi import APIRouter
from models import DiffResult
from pydantic import BaseModel
from typing import List

router = APIRouter()

class DiffRequest(BaseModel):
    base_text: str
    compare_text: str

@router.post("/diffs/", response_model=DiffResult)
def compute_diff(payload: DiffRequest):
    base_text = payload.base_text
    compare_text = payload.compare_text
    diffs = []
    words1 = base_text.split()
    words2 = compare_text.split()
    i, j = 0, 0
    while i < len(words1) or j < len(words2):
        if i < len(words1) and j < len(words2) and words1[i] == words2[j]:
            i += 1
            j += 1
        elif i < len(words1) and j < len(words2):
            diffs.append({"type": "change", "from": words1[i], "to": words2[j]})
            i += 1
            j += 1
        elif i < len(words1):
            diffs.append({"type": "deletion", "from": words1[i]})
            i += 1
        elif j < len(words2):
            diffs.append({"type": "insertion", "to": words2[j]})
            j += 1
    return DiffResult(base_text=base_text, compare_text=compare_text, diffs=diffs)
