"""Доменная сущность оценки статьи."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.domain.entities.base import BaseEntity


class Evaluation(BaseEntity):
    """Оценка статьи (peer-review карточка)."""
    
    def __init__(
        self,
        article_id: UUID,
        category: str,
        relevance: str,
        novelty_score: int,  # 1-5
        methodology_score: int,  # 1-5
        impact_score: int,  # 1-5
        overall_score: int,  # 1-5
        pros: List[str],
        cons: List[str],
        justification: str,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at)
        self.article_id = article_id
        self.category = category
        self.relevance = relevance
        self.novelty_score = novelty_score
        self.methodology_score = methodology_score
        self.impact_score = impact_score
        self.overall_score = overall_score
        self.pros = pros or []
        self.cons = cons or []
        self.justification = justification

