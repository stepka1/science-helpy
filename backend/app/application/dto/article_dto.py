"""DTO для работы со статьями."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class ArticleSearchResultDTO(BaseModel):
    """Результат поиска статьи."""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: Optional[datetime] = None
    categories: Optional[List[str]] = None
    pdf_url: Optional[str] = None
    tex_url: Optional[str] = None


class ArticleDTO(BaseModel):
    """DTO статьи."""
    id: UUID
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: Optional[datetime] = None
    categories: List[str] = []
    pdf_url: Optional[str] = None
    tex_url: Optional[str] = None
    local_pdf_path: Optional[str] = None
    local_tex_path: Optional[str] = None
    parsed_content: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

