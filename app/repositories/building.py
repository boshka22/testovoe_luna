"""Репозиторий зданий."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building as BuildingModel


class BuildingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[BuildingModel]:
        result = await self._session.execute(
            select(BuildingModel).order_by(BuildingModel.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, building_id: int) -> BuildingModel | None:
        result = await self._session.execute(
            select(BuildingModel).where(BuildingModel.id == building_id)
        )
        return result.scalar_one_or_none()
