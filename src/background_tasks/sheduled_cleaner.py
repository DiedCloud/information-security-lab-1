import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore

from src.common.di_container import di
from src.integration.repository.publication_repository import PublicationRepository
from src.service.generic.logger import logger


scheduler = AsyncIOScheduler(timezone="UTC")
JOB_ID = "cleaner_job"


def make_job_func():
    async def job():
        try:
            if asyncio.iscoroutinefunction(delete_old_entities):
                await delete_old_entities()
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, delete_old_entities)
        except Exception as e:
            logger.exception("Ошибка при выполнении задачи cleaner: %s", e)

    return job


async def delete_old_entities():
    async with di.pg_connection_provider.get_session() as session:
        repo = PublicationRepository(session)
        await repo.delete_old_entities()
