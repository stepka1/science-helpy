"""In-memory реализация репозитория оценок."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.domain.entities.evaluation import Evaluation
from app.domain.repositories.evaluation_repository import EvaluationRepository


class InMemoryEvaluationRepository(EvaluationRepository):
    """In-memory реализация репозитория оценок."""
    
    def __init__(self):
        self._evaluations: dict[UUID, Evaluation] = {}
        self._article_index: dict[UUID, UUID] = {}
    
    async def get_by_id(self, id: UUID) -> Optional[Evaluation]:
        return self._evaluations.get(id)
    
    async def get_by_article_id(self, article_id: UUID) -> Optional[Evaluation]:
        evaluation_id = self._article_index.get(article_id)
        if evaluation_id:
            return self._evaluations.get(evaluation_id)
        return None
    
    async def create(self, evaluation: Evaluation) -> Evaluation:
        self._evaluations[evaluation.id] = evaluation
        self._article_index[evaluation.article_id] = evaluation.id
        return evaluation
    
    async def update(self, evaluation: Evaluation) -> Evaluation:
        if evaluation.id in self._evaluations:
            self._evaluations[evaluation.id] = evaluation
            evaluation.updated_at = datetime.utcnow()
        return evaluation

