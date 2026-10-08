import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from file2formai.core.config import Settings


class Database:
    """Own the async engine, session factory, and process-level engine lifecycle."""

    def __init__(self, settings: Settings) -> None:
        self._readiness_timeout_seconds = settings.database_readiness_timeout_seconds
        self._engine: AsyncEngine = create_async_engine(
            settings.sqlalchemy_database_url,
            pool_pre_ping=True,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout_seconds,
            pool_recycle=1_800,
            connect_args={
                "timeout": settings.database_connect_timeout_seconds,
                "command_timeout": settings.database_readiness_timeout_seconds,
            },
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Yield a session while leaving transaction commits to application services."""

        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def ping(self) -> bool:
        async with asyncio.timeout(self._readiness_timeout_seconds):
            async with self._engine.connect() as connection:
                result = await connection.execute(text("SELECT 1"))
                return result.scalar_one() == 1

    async def dispose(self) -> None:
        await self._engine.dispose()
