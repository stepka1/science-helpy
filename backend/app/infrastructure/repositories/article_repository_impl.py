"""In-memory реализация репозитория статей."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from app.domain.entities.article import Article
from app.domain.repositories.article_repository import ArticleRepository


class InMemoryArticleRepository(ArticleRepository):
    """In-memory реализация репозитория статей (для тестирования/разработки)."""
    
    def __init__(self):
        self._articles: dict[UUID, Article] = {}
        self._arxiv_index: dict[str, UUID] = {}
    
    async def get_by_id(self, id: UUID) -> Optional[Article]:
        return self._articles.get(id)
    
    async def get_by_arxiv_id(self, arxiv_id: str) -> Optional[Article]:
        article_uuid = self._arxiv_index.get(arxiv_id)
        if article_uuid:
            return self._articles.get(article_uuid)
        return None
    
    async def get_all(self) -> List[Article]:
        return list(self._articles.values())
    
    async def create(self, article: Article) -> Article:
        self._articles[article.id] = article
        self._arxiv_index[article.arxiv_id] = article.id
        return article
    
    async def update(self, article: Article) -> Article:
        if article.id in self._articles:
            self._articles[article.id] = article
            article.updated_at = datetime.utcnow()
        return article
    
    async def delete(self, id: UUID) -> bool:
        if id in self._articles:
            article = self._articles[id]
            del self._articles[id]
            if article.arxiv_id in self._arxiv_index:
                del self._arxiv_index[article.arxiv_id]
            return True
        return False

