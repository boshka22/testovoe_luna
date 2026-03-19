"""ORM-модель деятельности (дерево с ограничением глубины 3 уровня)."""

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

MAX_DEPTH = 3


class Activity(Base):
    """Вид деятельности. Поддерживает вложенность до 3 уровней.

    Уровень 1 — корневые категории (Еда, Автомобили).
    Уровень 2 — подкатегории (Мясная продукция, Грузовые).
    Уровень 3 — листья (Запчасти, Аксессуары).
    """

    __tablename__ = "activities"
    __table_args__ = (
        CheckConstraint("level >= 1 AND level <= 3", name="ck_activity_level"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    parent: Mapped["Activity | None"] = relationship(
        "Activity", remote_side="Activity.id", back_populates="children"
    )
    children: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="parent", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name
