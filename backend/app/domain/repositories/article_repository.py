"""Интерфейс репозитория для статей."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.article import Article


class ArticleRepository(ABC):
    """Интерфейс репозитория для работы со статьями."""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Article]:
        """Получить статью по ID."""
        pass
    
    @abstractmethod
    async def get_by_arxiv_id(self, arxiv_id: str) -> Optional[Article]:
        """Получить статью по arXiv ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Article]:
        """Получить все статьи."""
        pass
    
    @abstractmethod
    async def create(self, article: Article) -> Article:
        """Создать новую статью."""
        pass
    
    @abstractmethod
    async def update(self, article: Article) -> Article:
        """Обновить статью."""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Удалить статью."""
        pass

