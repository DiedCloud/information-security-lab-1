from src.common.singleton import SingletonMeta
from src.integration.db_connection_provider import PGConnectionProvider


class DIContainer(metaclass=SingletonMeta):
    """
    Простейший контейнер для хранения провайдеров соединений и статики
    """
    pg_connection_provider: PGConnectionProvider

    def register_pg(self, connection_provider: type[PGConnectionProvider]):
        self.pg_connection_provider = connection_provider()

    def unregister_resources(self):
        del self.pg_connection_provider


di = DIContainer()
