"""Базовые классы для доменных сущностей."""
from abc import ABC
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class BaseEntity(ABC):
    """Базовая сущность домена."""
    
    def __init__(self, id: Optional[UUID] = None, created_at: Optional[datetime] = None):
        self.id: UUID = id or uuid4()
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: Optional[datetime] = None
    
    def __eq__(self, other):
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)

