from fastapi import APIRouter
from models import AICommentary
from pydantic import BaseModel

router = APIRouter()

class AICommentaryRequest(BaseModel):
    text_ref: str
    tradition: str = "Rashi"
    mode: str = "pshat"

@router.get("/ai/commentary/{text_ref}", response_model=AICommentary)
def get_ai_commentary(text_ref: str, tradition: str = "Rashi", mode: str = "pshat"):
    # Dummy implementation
    return AICommentary(
        text_ref=text_ref,
        tradition=tradition,
        mode=mode,
        generated=f"Example AI commentary on {text_ref} according to {tradition} ({mode})"
    )

@router.post("/ai/commentary/", response_model=AICommentary)
def ai_commentary_post(payload: AICommentaryRequest):
    # Dummy/stub for now
    return AICommentary(
        text_ref=payload.text_ref,
        tradition=payload.tradition,
        mode=payload.mode,
        generated=f"Generated (stub) AI commentary for {payload.text_ref} with {payload.tradition} ({payload.mode})"
    )
