"""DTO для оценок."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class EvaluationDTO(BaseModel):
    """DTO оценки статьи."""
    id: UUID
    article_id: UUID
    category: str
    relevance: str
    novelty_score: int
    methodology_score: int
    impact_score: int
    overall_score: int
    pros: List[str]
    cons: List[str]
    justification: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

