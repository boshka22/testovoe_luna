"""Pydantic-схемы для организаций."""

from pydantic import BaseModel, ConfigDict

from app.schemas.activity import ActivityResponse
from app.schemas.building import BuildingResponse


class PhoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phone: str


class OrganizationResponse(BaseModel):
    """Полная карточка организации."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: BuildingResponse
    phones: list[PhoneResponse]
    activities: list[ActivityResponse]


class OrganizationShortResponse(BaseModel):
    """Краткое представление для списков."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: BuildingResponse
    phones: list[PhoneResponse]


class PaginatedOrganizationsResponse(BaseModel):
    """Ответ со списком организаций и метаданными пагинации."""

    items: list[OrganizationShortResponse]
    total: int
    skip: int
    limit: int
