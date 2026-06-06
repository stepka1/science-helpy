"""Pydantic схемы для оценок."""
from typing import List
from pydantic import BaseModel, Field


class EvaluationResponse(BaseModel):
    """Ответ с оценкой статьи."""
    id: str
    article_id: str
    category: str
    relevance: str
    novelty_score: int = Field(..., ge=1, le=5)
    methodology_score: int = Field(..., ge=1, le=5)
    impact_score: int = Field(..., ge=1, le=5)
    overall_score: int = Field(..., ge=1, le=5)
    pros: List[str]
    cons: List[str]
    justification: str


class EvaluateArticleRequest(BaseModel):
    """Запрос на оценку статьи."""
    article_id: str = Field(..., description="UUID статьи")

