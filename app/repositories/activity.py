"""Репозиторий деятельностей."""

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_subtree_ids(self, root_id: int) -> list[int]:
        """Возвращает ID корневого узла и всех его потомков через рекурсивный CTE."""
        query = text(
            """
            WITH RECURSIVE tree AS (
                SELECT id FROM activities WHERE id = :root_id
                UNION ALL
                SELECT a.id FROM activities a
                JOIN tree t ON a.parent_id = t.id
            )
            SELECT id FROM tree
        """
        )
        result = await self._session.execute(query, {"root_id": root_id})
        return [row[0] for row in result.fetchall()]

    async def get_by_id(self, activity_id: int) -> Activity | None:
        result = await self._session.execute(
            select(Activity).where(Activity.id == activity_id)
        )
        return result.scalar_one_or_none()
