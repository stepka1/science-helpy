"""Use case для скачивания статьи через orchestration layer."""
from app.application.services.orchestration_service import OrchestrationService
from app.domain.entities.article import Article
from app.domain.repositories.article_repository import ArticleRepository
from app.shared.exceptions.base import NotFoundError


class DownloadArticleUseCase:
    """Use case для скачивания статьи через CoordinatorAgent."""

    def __init__(self, article_repository: ArticleRepository, orchestration_service: OrchestrationService):
        self.article_repository = article_repository
        self.orchestration_service = orchestration_service

    async def execute(self, arxiv_id: str) -> Article:
        existing_article = await self.article_repository.get_by_arxiv_id(arxiv_id)
        if existing_article:
            return existing_article

        article_data = await self.orchestration_service.download_article(arxiv_id)
        if not article_data:
            raise NotFoundError(f"Article with arXiv ID {arxiv_id} not found")

        article = Article(
            arxiv_id=article_data["arxiv_id"],
            title=article_data["title"],
            authors=article_data["authors"],
            abstract=article_data["abstract"],
            published_date=article_data["published_date"],
            categories=article_data["categories"],
            pdf_url=article_data["pdf_url"],
            tex_url=article_data["tex_url"],
            local_pdf_path=article_data["local_pdf_path"],
            local_tex_path=article_data["local_tex_path"],
        )
        return await self.article_repository.create(article)
