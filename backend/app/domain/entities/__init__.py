"""Доменные сущности."""
from app.domain.entities.base import BaseEntity
from app.domain.entities.article import Article
from app.domain.entities.evaluation import Evaluation
from app.domain.entities.review import Review

__all__ = ["BaseEntity", "Article", "Evaluation", "Review"]
