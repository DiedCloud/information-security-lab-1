from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings


class PGConnectionProvider:
    _engine: AsyncEngine
    _session_maker: async_sessionmaker[AsyncSession]

    def __init__(self):
        driver: str = "postgresql+asyncpg"
        db_url: str = (
            f"{driver}://{settings.PG_USERNAME}:{settings.PG_PASSWORD}"
            f"@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DATABASE}"
        )
        self._engine: AsyncEngine = create_async_engine(
            url=db_url,
            pool_size=settings.PG_POOL_SIZE,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=3600,
            pool_use_lifo=True,
            pool_pre_ping=True,
            isolation_level="REPEATABLE READ",
        )
        self._session_maker = async_sessionmaker(bind=self._engine)

    def get_connection(self) -> AsyncConnection:
        return self._engine.connect()

    def get_session(self) -> AsyncSession:
        return self._session_maker()

    async def close_connection_pool(self):
        await self._engine.dispose(close=True)
