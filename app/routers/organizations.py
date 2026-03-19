"""Роутер для организаций."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import verify_api_key
from app.exceptions import ConflictingFiltersError
from app.schemas.organization import (
    OrganizationResponse,
    OrganizationShortResponse,
    PaginatedOrganizationsResponse,
)
from app.services.organization import OrganizationService

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
    dependencies=[Depends(verify_api_key)],
)


def get_service(session: AsyncSession = Depends(get_session)) -> OrganizationService:
    return OrganizationService(session)


def _check_conflicting_filters(**kwargs: object) -> None:
    """Возбуждает 400 если передано более одного фильтра одновременно."""
    active = [name for name, value in kwargs.items() if value]
    if len(active) > 1:
        raise ConflictingFiltersError(
            f"Conflicting filters: {', '.join(active)}. Use only one at a time."
        )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int,
    service: OrganizationService = Depends(get_service),
) -> OrganizationResponse:
    """Карточка организации по ID."""
    org = await service.get_by_id(org_id)
    return OrganizationResponse.model_validate(org)


@router.get("", response_model=PaginatedOrganizationsResponse)
async def list_organizations(
    building_id: int | None = Query(default=None, description="Фильтр по зданию"),
    activity_id: int | None = Query(
        default=None,
        description="Фильтр по виду деятельности (включая дочерние)",
    ),
    search: str | None = Query(
        default=None, min_length=1, description="Поиск по названию"
    ),
    lat: float | None = Query(default=None, description="Широта центра"),
    lon: float | None = Query(default=None, description="Долгота центра"),
    radius_km: float | None = Query(
        default=None, gt=0, description="Радиус поиска в км"
    ),
    min_lat: float | None = Query(
        default=None, description="Мин. широта (прямоугольник)"
    ),
    max_lat: float | None = Query(
        default=None, description="Макс. широта (прямоугольник)"
    ),
    min_lon: float | None = Query(
        default=None, description="Мин. долгота (прямоугольник)"
    ),
    max_lon: float | None = Query(
        default=None, description="Макс. долгота (прямоугольник)"
    ),
    skip: int = Query(default=0, ge=0, description="Смещение для пагинации"),
    limit: int = Query(default=20, ge=1, le=100, description="Кол-во записей"),
    service: OrganizationService = Depends(get_service),
) -> PaginatedOrganizationsResponse:
    """Список организаций с фильтрацией и пагинацией.

    Допускается **ровно один** фильтр за раз. При передаче нескольких
    взаимоисключающих фильтров возвращается **400 Bad Request**.

    Доступные фильтры:
    - **building_id** — организации в конкретном здании
    - **activity_id** — по виду деятельности (включает все дочерние категории)
    - **search** — поиск по названию без учёта регистра
    - **lat + lon + radius_km** — в радиусе от точки
    - **min_lat + max_lat + min_lon + max_lon** — в прямоугольной области
    """
    radius_active = lat is not None and lon is not None and radius_km is not None
    bbox_active = all(x is not None for x in (min_lat, max_lat, min_lon, max_lon))

    _check_conflicting_filters(
        building_id=building_id,
        activity_id=activity_id,
        search=search,
        radius=radius_active or None,
        bbox=bbox_active or None,
    )

    if any(x is not None for x in (lat, lon, radius_km)) and not radius_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для поиска по радиусу требуются lat, lon и radius_km.",
        )

    if (
        any(x is not None for x in (min_lat, max_lat, min_lon, max_lon))
        and not bbox_active
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Для поиска по прямоугольнику требуются "
                "min_lat, max_lat, min_lon, max_lon."
            ),
        )

    if bbox_active and (min_lat >= max_lat or min_lon >= max_lon):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_lat должен быть меньше max_lat, min_lon — меньше max_lon.",
        )

    if building_id is not None:
        orgs = await service.get_by_building(building_id)
    elif activity_id is not None:
        orgs = await service.get_by_activity(activity_id)
    elif search is not None:
        orgs = await service.search_by_name(search)
    elif radius_active:
        orgs = await service.get_in_radius(lat, lon, radius_km)  # type: ignore
    elif bbox_active:
        orgs = await service.get_in_bbox(
            min_lat, max_lat, min_lon, max_lon  # type: ignore
        )
    else:
        orgs = []

    total = len(orgs)
    page = orgs[skip : skip + limit]

    return PaginatedOrganizationsResponse(
        items=[OrganizationShortResponse.model_validate(o) for o in page],
        total=total,
        skip=skip,
        limit=limit,
    )
