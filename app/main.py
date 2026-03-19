"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.exceptions import register_exception_handlers
from app.routers.buildings import router as buildings_router
from app.routers.organizations import router as organizations_router

app = FastAPI(
    title="Organization Directory API",
    description="Справочник организаций с поиском по зданию, деятельности и геопозиции",
    version="1.0.0",
)

register_exception_handlers(app)
app.include_router(buildings_router)
app.include_router(organizations_router)


@app.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})
