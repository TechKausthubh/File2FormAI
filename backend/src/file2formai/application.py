from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from file2formai.api.routes import router
from file2formai.core.config import Settings, get_settings
from file2formai.core.database import Database
from file2formai.core.errors import ApplicationError
from file2formai.core.logging import configure_logging
from file2formai.services.readiness import ReadinessService


def create_app(
    settings: Settings | None = None,
    readiness_service: ReadinessService | None = None,
    database: Database | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_database = database or Database(resolved_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging(resolved_settings.log_level)
        app.state.settings = resolved_settings
        app.state.database = resolved_database
        app.state.readiness_service = readiness_service or ReadinessService(resolved_database)
        try:
            yield
        finally:
            await resolved_database.dispose()

    application = FastAPI(
        title=resolved_settings.application_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "X-Development-Organization-ID"],
    )

    @application.exception_handler(ApplicationError)
    async def handle_application_error(
        _request: Request,
        error: ApplicationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"detail": error.detail},
        )

    application.include_router(router)
    return application
