from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.singleton import SingletonMeta
from src.integration.db_connection_provider import PGConnectionProvider


class DIContainer(metaclass=SingletonMeta):
    """
    Простейший контейнер для хранения провайдеров соединений и статики
    """

    pg_connection_provider: PGConnectionProvider

    def register_pg(self, connection_provider: type[PGConnectionProvider]):
        self.pg_connection_provider = connection_provider()

    async def get_pg_session(self) -> AsyncGenerator[AsyncSession]:
        """
        Предоставляет AsyncSession как dependency. Закрывает сессию автоматически.
        """
        async with self.pg_connection_provider.get_session() as session:
            yield session

    def unregister_resources(self):
        del self.pg_connection_provider


di = DIContainer()
