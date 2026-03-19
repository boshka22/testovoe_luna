#!/bin/sh
set -e

echo "==> Waiting for PostgreSQL..."
python << 'PYEOF'
import os, sys, time
import asyncpg
import asyncio

async def wait():
    for attempt in range(1, 31):
        try:
            conn = await asyncpg.connect(
                host=os.environ.get("POSTGRES_HOST", "db"),
                port=int(os.environ.get("POSTGRES_PORT", "5432")),
                user=os.environ.get("POSTGRES_USER", "postgres"),
                password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
                database=os.environ.get("POSTGRES_DB", "org_directory"),
            )
            await conn.close()
            print(f"PostgreSQL is ready (attempt {attempt}).")
            return
        except Exception:
            print(f"Attempt {attempt}/30: not ready, retrying in 2s...")
            await asyncio.sleep(2)
    print("PostgreSQL did not become available. Aborting.")
    sys.exit(1)

asyncio.run(wait())
PYEOF

echo "==> Running migrations..."
alembic upgrade head

echo "==> Starting application..."
exec "$@"
