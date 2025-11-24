from pydantic import BaseModel
from typing import Optional, List

class UploadResponse(BaseModel):
    id: str
    url: str

class SearchResult(BaseModel):
    id: str
    url: str
    score: float
