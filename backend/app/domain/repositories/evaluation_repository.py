"""Интерфейс репозитория для оценок."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.evaluation import Evaluation


class EvaluationRepository(ABC):
    """Интерфейс репозитория для работы с оценками."""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Evaluation]:
        """Получить оценку по ID."""
        pass
    
    @abstractmethod
    async def get_by_article_id(self, article_id: UUID) -> Optional[Evaluation]:
        """Получить оценку по ID статьи."""
        pass
    
    @abstractmethod
    async def create(self, evaluation: Evaluation) -> Evaluation:
        """Создать новую оценку."""
        pass
    
    @abstractmethod
    async def update(self, evaluation: Evaluation) -> Evaluation:
        """Обновить оценку."""
        pass

