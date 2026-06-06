"""Доменная сущность статьи."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.domain.entities.base import BaseEntity


class Article(BaseEntity):
    """Статья из arXiv."""
    
    def __init__(
        self,
        arxiv_id: str,
        title: str,
        authors: List[str],
        abstract: str,
        published_date: Optional[datetime] = None,
        categories: Optional[List[str]] = None,
        pdf_url: Optional[str] = None,
        tex_url: Optional[str] = None,
        local_pdf_path: Optional[str] = None,
        local_tex_path: Optional[str] = None,
        parsed_content: Optional[str] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at)
        self.arxiv_id = arxiv_id
        self.title = title
        self.authors = authors or []
        self.abstract = abstract
        self.published_date = published_date
        self.categories = categories or []
        self.pdf_url = pdf_url
        self.tex_url = tex_url
        self.local_pdf_path = local_pdf_path
        self.local_tex_path = local_tex_path
        self.parsed_content = parsed_content

