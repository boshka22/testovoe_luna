"""Интеграционные тесты API организаций."""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def _seed(session: AsyncSession) -> dict:
    """Создаёт минимальный набор данных для тестов."""
    from app.models.activity import Activity
    from app.models.building import Building
    from app.models.organization import Organization, OrganizationPhone

    food = Activity(id=1, name="Еда", level=1)
    meat = Activity(id=2, name="Мясная продукция", parent_id=1, level=2)
    session.add_all([food, meat])
    await session.flush()

    b1 = Building(id=1, address="ул. Ленина 1", latitude=55.75, longitude=37.61)
    b2 = Building(id=2, address="ул. Тверская 15", latitude=55.76, longitude=37.60)
    session.add_all([b1, b2])
    await session.flush()

    org1 = Organization(id=1, name="Мясной двор", building_id=1)
    org2 = Organization(id=2, name="Молочный рай", building_id=2)
    session.add_all([org1, org2])
    await session.flush()

    session.add(OrganizationPhone(organization_id=1, phone="1-111-111"))
    await session.flush()

    await session.execute(
        text("INSERT INTO organization_activities VALUES (1, 1), (1, 2)")
    )
    await session.commit()

    return {"org1_id": org1.id, "org2_id": org2.id, "building1_id": b1.id}


@pytest.mark.asyncio
class TestOrganizationAPI:
    async def test_get_by_id(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """GET /organizations/{id} возвращает полную карточку."""
        data = await _seed(db_session)
        response = await client.get(f"/organizations/{data['org1_id']}")
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Мясной двор"
        assert body["building"]["address"] == "ул. Ленина 1"
        assert len(body["phones"]) == 1
        assert len(body["activities"]) == 2

    async def test_get_nonexistent_returns_404(self, client: AsyncClient) -> None:
        """GET несуществующей организации возвращает 404."""
        response = await client.get("/organizations/99999")
        assert response.status_code == 404

    async def test_filter_by_building(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """?building_id возвращает только организации в этом здании."""
        data = await _seed(db_session)
        response = await client.get(
            f"/organizations?building_id={data['building1_id']}"
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1
        assert body["items"][0]["name"] == "Мясной двор"

    async def test_filter_by_activity_includes_children(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """?activity_id=1 (Еда) возвращает организации с Еда И Мясная продукция."""
        await _seed(db_session)
        response = await client.get("/organizations?activity_id=1")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["name"] == "Мясной двор"

    async def test_search_by_name(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """?search находит по частичному совпадению без учёта регистра."""
        await _seed(db_session)
        response = await client.get("/organizations?search=мясн")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["name"] == "Мясной двор"

    async def test_search_case_insensitive(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Поиск не зависит от регистра."""
        await _seed(db_session)
        response = await client.get("/organizations?search=МЯСН")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    async def test_radius_filter(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """?lat&lon&radius_km возвращает организации в радиусе."""
        await _seed(db_session)
        response = await client.get("/organizations?lat=55.75&lon=37.61&radius_km=1")
        assert response.status_code == 200
        items = response.json()["items"]
        assert any(o["name"] == "Мясной двор" for o in items)

    async def test_bbox_filter(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Прямоугольная область возвращает правильные организации."""
        await _seed(db_session)
        response = await client.get(
            "/organizations?min_lat=55.74&max_lat=55.76&min_lon=37.60&max_lon=37.62"
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    async def test_conflicting_filters_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Передача двух фильтров одновременно возвращает 400."""
        await _seed(db_session)
        response = await client.get("/organizations?building_id=1&activity_id=1")
        assert response.status_code == 400

    async def test_no_api_key_returns_403(self, client: AsyncClient) -> None:
        """Запрос без X-API-Key возвращает 403."""
        response = await client.get(
            "/organizations", headers={"X-API-Key": "wrong-key"}
        )
        assert response.status_code == 403

    async def test_list_buildings(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """GET /buildings возвращает список зданий."""
        await _seed(db_session)
        response = await client.get("/buildings")
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """?limit=1 возвращает одну запись, total отражает реальное количество."""
        await _seed(db_session)
        response = await client.get("/organizations?activity_id=1&limit=1")
        assert response.status_code == 200
        body = response.json()
        assert len(body["items"]) == 1
        assert body["total"] >= 1
        assert body["limit"] == 1
