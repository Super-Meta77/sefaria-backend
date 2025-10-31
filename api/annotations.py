from fastapi import APIRouter, HTTPException
from models import Annotation
from typing import List

router = APIRouter()

# In-memory store for demo
ANNOTATIONS = []

@router.get("/annotations/{text_ref}", response_model=List[Annotation])
def get_annotations(text_ref: str):
    """Get all annotations for a given text reference."""
    return [a for a in ANNOTATIONS if a.text_ref == text_ref]

@router.get("/annotations/user/{username}", response_model=List[Annotation])
def get_user_annotations(username: str):
    """Get all annotations from a user."""
    return [a for a in ANNOTATIONS if a.user == username]

@router.post("/annotations/", response_model=Annotation)
def add_annotation(annotation: Annotation):
    """Add a new annotation."""
    ANNOTATIONS.append(annotation)
    return annotation

@router.put("/annotations/{idx}", response_model=Annotation)
def edit_annotation(idx: int, annotation: Annotation):
    """Edit an annotation by index (demo use only)."""
    if idx < 0 or idx >= len(ANNOTATIONS):
        raise HTTPException(status_code=404, detail="Annotation not found")
    ANNOTATIONS[idx] = annotation
    return annotation

@router.delete("/annotations/{idx}")
def delete_annotation(idx: int):
    """Delete an annotation by index (demo use only)."""
    if idx < 0 or idx >= len(ANNOTATIONS):
        raise HTTPException(status_code=404, detail="Annotation not found")
    ANNOTATIONS.pop(idx)
    return {"removed": True, "index": idx}
