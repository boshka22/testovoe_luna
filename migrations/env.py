"""Конфигурация Alembic для асинхронных миграций."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.database import Base

# Импортируем все модели для регистрации в metadata
from app.models.activity import Activity  # noqa: F401
from app.models.building import Building  # noqa: F401
from app.models.organization import Organization, OrganizationPhone  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn, target_metadata=target_metadata
            )
        )
        async with connection.begin():
            await connection.run_sync(lambda _: context.run_migrations())
    await connectable.dispose()


if context.is_offline_mode():
    raise RuntimeError("Offline mode is not supported.")
else:
    asyncio.run(run_migrations_online())
