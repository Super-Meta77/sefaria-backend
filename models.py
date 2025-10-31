from pydantic import BaseModel
from typing import List, Optional

class Text(BaseModel):
    ref: str
    lang: Optional[str] = "he"
    content: str
    versions: Optional[List[str]] = None

class Connection(BaseModel):
    source: str
    target: str
    type: str
    strength: Optional[float]
    metadata: Optional[dict] = {}

class DiffResult(BaseModel):
    base_text: str
    compare_text: str
    diffs: List[dict]

class User(BaseModel):
    username: str
    email: str
    hashed_password: str
    is_active: bool = True

class Annotation(BaseModel):
    text_ref: str
    user: str
    layer: Optional[str] = None
    content: str
    selection: Optional[str] = None
    type: Optional[str] = "comment"

class AICommentary(BaseModel):
    text_ref: str
    tradition: str
    mode: str
    generated: str
