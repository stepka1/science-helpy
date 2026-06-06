"""Мапперы для конвертации между доменными сущностями и DTO."""
from app.domain.entities.article import Article
from app.domain.entities.evaluation import Evaluation
from app.domain.entities.review import Review
from app.application.dto.article_dto import ArticleDTO
from app.application.dto.evaluation_dto import EvaluationDTO
from app.application.dto.review_dto import ReviewDTO


def article_to_dto(article: Article) -> ArticleDTO:
    """Конвертировать Article в ArticleDTO."""
    return ArticleDTO(
        id=article.id,
        arxiv_id=article.arxiv_id,
        title=article.title,
        authors=article.authors,
        abstract=article.abstract,
        published_date=article.published_date,
        categories=article.categories,
        pdf_url=article.pdf_url,
        tex_url=article.tex_url,
        local_pdf_path=article.local_pdf_path,
        local_tex_path=article.local_tex_path,
        parsed_content=article.parsed_content,
        created_at=article.created_at,
        updated_at=article.updated_at
    )


def evaluation_to_dto(evaluation: Evaluation) -> EvaluationDTO:
    """Конвертировать Evaluation в EvaluationDTO."""
    return EvaluationDTO(
        id=evaluation.id,
        article_id=evaluation.article_id,
        category=evaluation.category,
        relevance=evaluation.relevance,
        novelty_score=evaluation.novelty_score,
        methodology_score=evaluation.methodology_score,
        impact_score=evaluation.impact_score,
        overall_score=evaluation.overall_score,
        pros=evaluation.pros,
        cons=evaluation.cons,
        justification=evaluation.justification,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at
    )


def review_to_dto(review: Review) -> ReviewDTO:
    """Конвертировать Review в ReviewDTO."""
    return ReviewDTO(
        id=review.id,
        article_id=review.article_id,
        summary=review.summary,
        methods=review.methods,
        results=review.results,
        criticism=review.criticism,
        application=review.application,
        verdict=review.verdict,
        full_text=review.full_text,
        created_at=review.created_at,
        updated_at=review.updated_at
    )

