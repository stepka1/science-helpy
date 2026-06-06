"""Обработка ошибок."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.shared.exceptions.base import DomainException, NotFoundError, ServiceUnavailableError, ValidationError


async def domain_exception_handler(request: Request, exc: DomainException):
    """Обработчик доменных исключений."""
    status_code = status.HTTP_400_BAD_REQUEST
    
    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, ServiceUnavailableError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc)
        }
    )
