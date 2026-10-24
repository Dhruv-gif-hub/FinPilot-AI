from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..core.config import config_value


class DatabaseFactory:
    """Factory responsible for creating database infrastructure."""

    @staticmethod
    def create_engine(database_url: str) -> AsyncEngine:
        return create_async_engine(
            database_url,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=False,
        )

    @staticmethod
    def create_session_maker(
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )

engine = DatabaseFactory.create_engine(
    config_value.Database_url
)

Session_local = DatabaseFactory.create_session_maker(
    engine
)