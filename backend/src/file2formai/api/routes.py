from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from file2formai.api.dependencies import get_readiness_service
from file2formai.api.equipment_routes import router as equipment_router
from file2formai.api.organization_routes import router as organization_router
from file2formai.services.readiness import ReadinessService

router = APIRouter(tags=["platform"])
router.include_router(organization_router)
router.include_router(equipment_router)


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    response_model=HealthResponse,
    responses={503: {"description": "A required dependency is unavailable"}},
)
async def ready(
    readiness_service: Annotated[ReadinessService, Depends(get_readiness_service)],
) -> HealthResponse | JSONResponse:
    if not await readiness_service.is_ready():
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return HealthResponse(status="ok")
