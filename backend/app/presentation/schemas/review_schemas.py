"""Pydantic схемы для обзоров."""
from pydantic import BaseModel, Field


class ReviewResponse(BaseModel):
    """Ответ с обзором статьи."""
    id: str
    article_id: str
    summary: str
    methods: str
    results: str
    criticism: str
    application: str
    verdict: str
    full_text: str


class WriteReviewRequest(BaseModel):
    """Запрос на написание обзора."""
    article_id: str = Field(..., description="UUID статьи")

