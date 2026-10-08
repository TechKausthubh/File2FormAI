from typing import Protocol

import structlog

logger = structlog.get_logger()


class DatabaseHealthProbe(Protocol):
    async def ping(self) -> bool: ...


class ReadinessService:
    """Translate infrastructure availability into a safe application readiness result."""

    def __init__(self, database: DatabaseHealthProbe) -> None:
        self._database = database

    async def is_ready(self) -> bool:
        try:
            return await self._database.ping()
        # A health boundary must return a safe result for any driver failure.
        except Exception as error:
            await logger.awarning(
                "database_readiness_failed",
                error_type=type(error).__name__,
            )
            return False
