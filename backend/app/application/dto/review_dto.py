"""DTO для обзоров."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ReviewDTO(BaseModel):
    """DTO обзора статьи."""
    id: UUID
    article_id: UUID
    summary: str
    methods: str
    results: str
    criticism: str
    application: str
    verdict: str
    full_text: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

