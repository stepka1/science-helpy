"""Интерфейс репозитория для обзоров."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.review import Review


class ReviewRepository(ABC):
    """Интерфейс репозитория для работы с обзорами."""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Review]:
        """Получить обзор по ID."""
        pass
    
    @abstractmethod
    async def get_by_article_id(self, article_id: UUID) -> Optional[Review]:
        """Получить обзор по ID статьи."""
        pass
    
    @abstractmethod
    async def create(self, review: Review) -> Review:
        """Создать новый обзор."""
        pass
    
    @abstractmethod
    async def update(self, review: Review) -> Review:
        """Обновить обзор."""
        pass

