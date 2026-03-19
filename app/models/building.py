"""ORM-модель здания."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organization import Organization


class Building(Base):
    """Здание с адресом и географическими координатами."""

    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    organizations: Mapped[list[Organization]] = relationship(
        "Organization", back_populates="building"
    )

    def __str__(self) -> str:
        return self.address
