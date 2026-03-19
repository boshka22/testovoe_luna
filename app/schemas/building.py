"""Pydantic-схемы для зданий."""

from pydantic import BaseModel, ConfigDict


class BuildingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    latitude: float
    longitude: float
