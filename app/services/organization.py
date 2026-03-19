"""Сервисный слой для организаций."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.organization import Organization
from app.repositories.activity import ActivityRepository
from app.repositories.building import BuildingRepository
from app.repositories.organization import OrganizationRepository


class OrganizationService:
    def __init__(self, session: AsyncSession) -> None:
        self._orgs = OrganizationRepository(session)
        self._activities = ActivityRepository(session)
        self._buildings = BuildingRepository(session)

    async def get_by_id(self, org_id: int) -> Organization:
        org = await self._orgs.get_by_id(org_id)
        if org is None:
            raise NotFoundError("Organization", org_id)
        return org

    async def get_by_building(self, building_id: int) -> list[Organization]:
        building = await self._buildings.get_by_id(building_id)
        if building is None:
            raise NotFoundError("Building", building_id)
        return await self._orgs.get_by_building(building_id)

    async def get_by_activity(self, activity_id: int) -> list[Organization]:
        """Возвращает организации по виду деятельности включая все дочерние."""
        activity = await self._activities.get_by_id(activity_id)
        if activity is None:
            raise NotFoundError("Activity", activity_id)
        ids = await self._activities.get_subtree_ids(activity_id)
        return await self._orgs.get_by_activity_ids(ids)

    async def search_by_name(self, query: str) -> list[Organization]:
        return await self._orgs.search_by_name(query)

    async def get_in_radius(
        self, lat: float, lon: float, radius_km: float
    ) -> list[Organization]:
        return await self._orgs.get_in_radius(lat, lon, radius_km)

    async def get_in_bbox(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
    ) -> list[Organization]:
        return await self._orgs.get_in_bbox(min_lat, max_lat, min_lon, max_lon)
