"""Доменная сущность обзора статьи."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.domain.entities.base import BaseEntity


class Review(BaseEntity):
    """Обзор статьи на русском языке."""
    
    def __init__(
        self,
        article_id: UUID,
        summary: str,
        methods: str,
        results: str,
        criticism: str,
        application: str,
        verdict: str,
        full_text: str,  # Полный текст обзора в Markdown
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at)
        self.article_id = article_id
        self.summary = summary
        self.methods = methods
        self.results = results
        self.criticism = criticism
        self.application = application
        self.verdict = verdict
        self.full_text = full_text

