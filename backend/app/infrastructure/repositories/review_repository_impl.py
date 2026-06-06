"""In-memory реализация репозитория обзоров."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.domain.entities.review import Review
from app.domain.repositories.review_repository import ReviewRepository


class InMemoryReviewRepository(ReviewRepository):
    """In-memory реализация репозитория обзоров."""
    
    def __init__(self):
        self._reviews: dict[UUID, Review] = {}
        self._article_index: dict[UUID, UUID] = {}
    
    async def get_by_id(self, id: UUID) -> Optional[Review]:
        return self._reviews.get(id)
    
    async def get_by_article_id(self, article_id: UUID) -> Optional[Review]:
        review_id = self._article_index.get(article_id)
        if review_id:
            return self._reviews.get(review_id)
        return None
    
    async def create(self, review: Review) -> Review:
        self._reviews[review.id] = review
        self._article_index[review.article_id] = review.id
        return review
    
    async def update(self, review: Review) -> Review:
        if review.id in self._reviews:
            self._reviews[review.id] = review
            review.updated_at = datetime.utcnow()
        return review

