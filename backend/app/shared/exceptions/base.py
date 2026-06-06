"""Базовые исключения."""
from typing import Optional


class DomainException(Exception):
    """Базовое исключение домена."""
    pass


class NotFoundError(DomainException):
    """Исключение когда сущность не найдена."""
    
    def __init__(self, message: str = "Entity not found", entity_name: Optional[str] = None):
        self.entity_name = entity_name
        super().__init__(message)


class ValidationError(DomainException):
    """Исключение валидации."""
    pass


class RepositoryError(DomainException):
    """Исключение репозитория."""
    pass


class ServiceUnavailableError(DomainException):
    """Исключение недоступности внешнего сервиса."""
    pass
