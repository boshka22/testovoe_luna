"""Репозиторий организаций."""

import math
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.building import Building as BuildingModel
from app.models.organization import Organization, organization_activities


def _with_relations() -> list[Any]:
    """Загружает связанные объекты одним запросом (избегает N+1)."""
    return [
        selectinload(Organization.building),
        selectinload(Organization.phones),
        selectinload(Organization.activities),
    ]


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, org_id: int) -> Organization | None:
        result = await self._session.execute(
            select(Organization)
            .options(*_with_relations())
            .where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_by_building(self, building_id: int) -> list[Organization]:
        result = await self._session.execute(
            select(Organization)
            .options(*_with_relations())
            .where(Organization.building_id == building_id)
            .order_by(Organization.name)
        )
        return list(result.scalars().all())

    async def get_by_activity_ids(self, activity_ids: list[int]) -> list[Organization]:
        """Возвращает организации, связанные с любым из указанных ID деятельностей."""
        result = await self._session.execute(
            select(Organization)
            .options(*_with_relations())
            .join(
                organization_activities,
                Organization.id == organization_activities.c.organization_id,
            )
            .where(organization_activities.c.activity_id.in_(activity_ids))
            .distinct()
            .order_by(Organization.name)
        )
        return list(result.scalars().all())

    async def search_by_name(self, query: str) -> list[Organization]:
        """Поиск по названию без учёта регистра (ILIKE)."""
        result = await self._session.execute(
            select(Organization)
            .options(*_with_relations())
            .where(Organization.name.ilike(f"%{query}%"))
            .order_by(Organization.name)
        )
        return list(result.scalars().all())

    async def get_in_radius(
        self, lat: float, lon: float, radius_km: float
    ) -> list[Organization]:
        """Возвращает организации в радиусе от точки (формула Haversine)."""
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

        result = await self._session.execute(
            select(Organization)
            .options(*_with_relations())
            .join(BuildingModel, Organization.building_id == BuildingModel.id)
            .where(
                and_(
                    BuildingModel.latitude.between(lat - lat_delta, lat + lat_delta),
                    BuildingModel.longitude.between(lon - lon_delta, lon + lon_delta),
                )
            )
        )
        candidates = list(result.scalars().all())

        return [
            org
            for org in candidates
            if _haversine(lat, lon, org.building.latitude, org.building.longitude)
            <= radius_km
        ]

    async def get_in_bbox(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
    ) -> list[Organization]:
        """Возвращает организации в прямоугольной области."""
        result = await self._session.execute(
            select(Organization)
            .options(*_with_relations())
            .join(BuildingModel, Organization.building_id == BuildingModel.id)
            .where(
                and_(
                    BuildingModel.latitude.between(min_lat, max_lat),
                    BuildingModel.longitude.between(min_lon, max_lon),
                )
            )
            .order_by(Organization.name)
        )
        return list(result.scalars().all())


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Вычисляет расстояние между двумя точками в километрах."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.asin(math.sqrt(a))
