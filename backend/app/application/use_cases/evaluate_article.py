"""Use case для оценки статьи через GraphMAS."""
from uuid import UUID

from app.application.dto.evaluation_dto import EvaluationDTO
from app.application.dto.mappers import evaluation_to_dto
from app.application.services.orchestration_service import OrchestrationService
from app.domain.repositories.article_repository import ArticleRepository
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.shared.exceptions.base import NotFoundError


class EvaluateArticleUseCase:
    """Use case для оценки статьи через единый orchestration layer."""

    def __init__(
        self,
        article_repository: ArticleRepository,
        evaluation_repository: EvaluationRepository,
        orchestration_service: OrchestrationService,
    ):
        self.article_repository = article_repository
        self.evaluation_repository = evaluation_repository
        self.orchestration_service = orchestration_service

    async def execute(self, article_id: UUID) -> EvaluationDTO:
        existing_evaluation = await self.evaluation_repository.get_by_article_id(article_id)
        if existing_evaluation:
            return evaluation_to_dto(existing_evaluation)

        article = await self.article_repository.get_by_id(article_id)
        if not article:
            raise NotFoundError(f"Article with ID {article_id} not found")

        evaluation_dto, orchestration_state = await self.orchestration_service.evaluate_article(article)
        article.parsed_content = orchestration_state.get("parsed_content") or article.parsed_content
        if orchestration_state.get("selected_paper_path"):
            selected_path = orchestration_state["selected_paper_path"]
            if str(selected_path).endswith(".pdf"):
                article.local_pdf_path = selected_path
            else:
                article.local_tex_path = selected_path
        await self.article_repository.update(article)

        from app.domain.entities.evaluation import Evaluation

        evaluation = Evaluation(
            article_id=evaluation_dto.article_id,
            category=evaluation_dto.category,
            relevance=evaluation_dto.relevance,
            novelty_score=evaluation_dto.novelty_score,
            methodology_score=evaluation_dto.methodology_score,
            impact_score=evaluation_dto.impact_score,
            overall_score=evaluation_dto.overall_score,
            pros=evaluation_dto.pros,
            cons=evaluation_dto.cons,
            justification=evaluation_dto.justification,
        )
        saved_evaluation = await self.evaluation_repository.create(evaluation)
        return evaluation_to_dto(saved_evaluation)
