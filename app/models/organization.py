"""ORM-модели организации."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.building import Building

organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        BigInteger,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        BigInteger,
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class OrganizationPhone(Base):
    """Телефонный номер организации."""

    __tablename__ = "organization_phones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    phone: Mapped[str] = mapped_column(String(50), nullable=False)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="phones"
    )


class Organization(Base):
    """Карточка организации в справочнике."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    building_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("buildings.id", ondelete="RESTRICT"),
        index=True,
    )

    building: Mapped[Building] = relationship(
        "Building", back_populates="organizations"
    )
    phones: Mapped[list[OrganizationPhone]] = relationship(
        "OrganizationPhone",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list[Activity]] = relationship(
        "Activity",
        secondary=organization_activities,
    )

    def __str__(self) -> str:
        return self.name
