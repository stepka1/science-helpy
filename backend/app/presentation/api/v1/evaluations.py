"""API endpoints для оценок статей."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.application.use_cases import EvaluateArticleUseCase
from app.application.dto.mappers import evaluation_to_dto
from app.presentation.dependencies import (
    get_article_repository,
    get_evaluation_repository,
    get_orchestration_service
)
from app.presentation.schemas import EvaluationResponse, EvaluateArticleRequest
from app.shared.exceptions.base import NotFoundError

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_article(
    request: EvaluateArticleRequest,
    article_repository=Depends(get_article_repository),
    evaluation_repository=Depends(get_evaluation_repository),
    orchestration_service=Depends(get_orchestration_service)
):
    """
    Оценить статью.

    Args:
        request: Параметры оценки
        article_repository: Репозиторий статей
        evaluation_repository: Репозиторий оценок
    
    Returns:
        Структурированная оценка статьи
    """
    try:
        article_uuid = UUID(request.article_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid article ID format"
        )
    
    use_case = EvaluateArticleUseCase(
        article_repository,
        evaluation_repository,
        orchestration_service
    )
    
    try:
        evaluation_dto = await use_case.execute(article_uuid)
        return EvaluationResponse(
            id=str(evaluation_dto.id),
            article_id=str(evaluation_dto.article_id),
            category=evaluation_dto.category,
            relevance=evaluation_dto.relevance,
            novelty_score=evaluation_dto.novelty_score,
            methodology_score=evaluation_dto.methodology_score,
            impact_score=evaluation_dto.impact_score,
            overall_score=evaluation_dto.overall_score,
            pros=evaluation_dto.pros,
            cons=evaluation_dto.cons,
            justification=evaluation_dto.justification
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/article/{article_id}", response_model=EvaluationResponse)
async def get_evaluation_by_article(
    article_id: str,
    evaluation_repository=Depends(get_evaluation_repository)
):
    """
    Получить оценку статьи.
    
    Args:
        article_id: UUID статьи
        evaluation_repository: Репозиторий оценок
    
    Returns:
        Оценка статьи
    """
    try:
        article_uuid = UUID(article_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid article ID format"
        )
    
    evaluation = await evaluation_repository.get_by_article_id(article_uuid)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    dto = evaluation_to_dto(evaluation)
    return EvaluationResponse(
        id=str(dto.id),
        article_id=str(dto.article_id),
        category=dto.category,
        relevance=dto.relevance,
        novelty_score=dto.novelty_score,
        methodology_score=dto.methodology_score,
        impact_score=dto.impact_score,
        overall_score=dto.overall_score,
        pros=dto.pros,
        cons=dto.cons,
        justification=dto.justification
    )
