"""Сервисный слой для деятельностей."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.activity import MAX_DEPTH, Activity
from app.repositories.activity import ActivityRepository


class ActivityDepthError(Exception):
    """Превышена максимальная глубина вложенности деятельностей."""

    def __init__(self) -> None:
        super().__init__(
            f"Максимальная глубина вложенности деятельностей — {MAX_DEPTH} уровня."
        )


class ActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ActivityRepository(session)
        self._session = session

    async def create(self, name: str, parent_id: int | None = None) -> Activity:
        """Создаёт новый вид деятельности с проверкой глубины вложенности.

        Args:
            name: Название деятельности.
            parent_id: ID родительской деятельности или None для корневой.

        Raises:
            NotFoundError: Родительская деятельность не найдена.
            ActivityDepthError: Превышен лимит в MAX_DEPTH уровней.
        """
        level = 1

        if parent_id is not None:
            parent = await self._repo.get_by_id(parent_id)
            if parent is None:
                raise NotFoundError("Activity", parent_id)

            level = parent.level + 1
            if level > MAX_DEPTH:
                raise ActivityDepthError()

        activity = Activity(name=name, parent_id=parent_id, level=level)
        self._session.add(activity)
        await self._session.commit()
        await self._session.refresh(activity)
        return activity
