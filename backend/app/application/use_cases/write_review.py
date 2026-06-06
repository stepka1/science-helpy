"""Use case для написания обзора статьи через GraphMAS."""
from uuid import UUID

from app.application.dto.mappers import review_to_dto
from app.application.dto.review_dto import ReviewDTO
from app.application.services.orchestration_service import OrchestrationService
from app.domain.repositories.article_repository import ArticleRepository
from app.domain.repositories.review_repository import ReviewRepository
from app.shared.exceptions.base import NotFoundError


class WriteReviewUseCase:
    """Use case для написания обзора через единый orchestration layer."""

    def __init__(
        self,
        article_repository: ArticleRepository,
        review_repository: ReviewRepository,
        orchestration_service: OrchestrationService,
    ):
        self.article_repository = article_repository
        self.review_repository = review_repository
        self.orchestration_service = orchestration_service

    async def execute(self, article_id: UUID) -> ReviewDTO:
        existing_review = await self.review_repository.get_by_article_id(article_id)
        if existing_review:
            return review_to_dto(existing_review)

        article = await self.article_repository.get_by_id(article_id)
        if not article:
            raise NotFoundError(f"Article with ID {article_id} not found")

        review_dto, orchestration_state = await self.orchestration_service.write_review(article)
        article.parsed_content = orchestration_state.get("parsed_content") or article.parsed_content
        if orchestration_state.get("selected_paper_path"):
            selected_path = orchestration_state["selected_paper_path"]
            if str(selected_path).endswith(".pdf"):
                article.local_pdf_path = selected_path
            else:
                article.local_tex_path = selected_path
        await self.article_repository.update(article)

        from app.domain.entities.review import Review

        review = Review(
            article_id=review_dto.article_id,
            summary=review_dto.summary,
            methods=review_dto.methods,
            results=review_dto.results,
            criticism=review_dto.criticism,
            application=review_dto.application,
            verdict=review_dto.verdict,
            full_text=review_dto.full_text,
        )
        saved_review = await self.review_repository.create(review)
        return review_to_dto(saved_review)
