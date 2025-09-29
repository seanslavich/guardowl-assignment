from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel

class SecurityReport(BaseModel):
    id: str
    siteId: str
    date: datetime
    guardId: str
    text: str

class QueryRequest(BaseModel):
    query: str
    siteId: Optional[str] = None
    dateRange: Optional[Dict[str, str]] = None  # {"start": "2025-08-01", "end": "2025-08-31"}

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]