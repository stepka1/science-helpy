"""Базовые интерфейсы репозиториев."""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Базовый интерфейс репозитория."""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Получить сущность по ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Получить все сущности."""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Создать новую сущность."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Обновить сущность."""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Удалить сущность по ID."""
        pass

