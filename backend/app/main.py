"""Главный файл приложения FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.config.settings import settings
from app.presentation.api import api_router
from app.presentation.middleware.error_handler import domain_exception_handler
from app.shared.exceptions.base import DomainException


def create_app() -> FastAPI:
    """Создание и настройка приложения FastAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )
    
    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Регистрация обработчика исключений
    app.add_exception_handler(DomainException, domain_exception_handler)
    
    # Подключение роутеров
    app.include_router(api_router)
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

