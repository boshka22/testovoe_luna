"""Роутер для зданий."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import verify_api_key
from app.repositories.building import BuildingRepository
from app.schemas.building import BuildingResponse

router = APIRouter(
    prefix="/buildings",
    tags=["buildings"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=list[BuildingResponse])
async def list_buildings(
    skip: int = Query(default=0, ge=0, description="Пропустить N записей"),
    limit: int = Query(default=20, ge=1, le=100, description="Максимум записей"),
    session: AsyncSession = Depends(get_session),
) -> list[BuildingResponse]:
    """Список всех зданий с пагинацией."""
    repo = BuildingRepository(session)
    buildings = await repo.get_all(skip=skip, limit=limit)
    return [BuildingResponse.model_validate(b) for b in buildings]
