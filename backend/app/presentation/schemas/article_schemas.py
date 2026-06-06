"""Pydantic схемы для работы со статьями."""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchArticlesRequest(BaseModel):
    """Запрос на поиск статей."""
    query: str = Field(..., description="Поисковый запрос")
    max_results: int = Field(10, ge=1, le=100, description="Максимальное количество результатов")


class DownloadArticleRequest(BaseModel):
    """Запрос на скачивание статьи."""
    arxiv_id: str = Field(..., description="arXiv ID статьи (например, '2501.12345')")


class ParseArticleRequest(BaseModel):
    """Запрос на парсинг статьи."""
    article_id: str = Field(..., description="UUID статьи")


class ArticleResponse(BaseModel):
    """Ответ с информацией о статье."""
    id: str
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: Optional[str] = None
    categories: List[str] = []
    pdf_url: Optional[str] = None
    tex_url: Optional[str] = None
    local_pdf_path: Optional[str] = None
    local_tex_path: Optional[str] = None
    parsed_content: Optional[str] = None

