"""API endpoints для обзоров статей."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.application.use_cases import WriteReviewUseCase
from app.application.dto.mappers import review_to_dto
from app.presentation.dependencies import (
    get_article_repository,
    get_review_repository,
    get_orchestration_service
)
from app.presentation.schemas import ReviewResponse, WriteReviewRequest
from app.shared.exceptions.base import NotFoundError

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/write", response_model=ReviewResponse)
async def write_review(
    request: WriteReviewRequest,
    article_repository=Depends(get_article_repository),
    review_repository=Depends(get_review_repository),
    orchestration_service=Depends(get_orchestration_service)
):
    """
    Написать обзор статьи.

    Args:
        request: Параметры обзора
        article_repository: Репозиторий статей
        review_repository: Репозиторий обзоров

    Returns:
        Обзор статьи на русском языке
    """
    try:
        article_uuid = UUID(request.article_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid article ID format"
        )
    
    use_case = WriteReviewUseCase(
        article_repository,
        review_repository,
        orchestration_service
    )
    
    try:
        review_dto = await use_case.execute(article_uuid)
        return ReviewResponse(
            id=str(review_dto.id),
            article_id=str(review_dto.article_id),
            summary=review_dto.summary,
            methods=review_dto.methods,
            results=review_dto.results,
            criticism=review_dto.criticism,
            application=review_dto.application,
            verdict=review_dto.verdict,
            full_text=review_dto.full_text
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/article/{article_id}", response_model=ReviewResponse)
async def get_review_by_article(
    article_id: str,
    review_repository=Depends(get_review_repository)
):
    """
    Получить обзор статьи.
    
    Args:
        article_id: UUID статьи
        review_repository: Репозиторий обзоров
    
    Returns:
        Обзор статьи
    """
    try:
        article_uuid = UUID(article_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid article ID format"
        )
    
    review = await review_repository.get_by_article_id(article_uuid)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    dto = review_to_dto(review)
    return ReviewResponse(
        id=str(dto.id),
        article_id=str(dto.article_id),
        summary=dto.summary,
        methods=dto.methods,
        results=dto.results,
        criticism=dto.criticism,
        application=dto.application,
        verdict=dto.verdict,
        full_text=dto.full_text
    )
