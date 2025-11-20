from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.integration.repository.entity import Publication
from src.integration.repository.publication_repository import PublicationRepository


async def service_list_publications(
    repo: PublicationRepository,
    limit: int = 50,
    offset: int = 0,
) -> list[Publication]:
    return await repo.list(limit=limit, offset=offset)


async def service_get_publication(
    repo: PublicationRepository,
    pub_id: int,
) -> Optional[Publication]:
    return await repo.get_by_id(pub_id)


async def service_create_publication(session: AsyncSession, title: str, content: str, author_id: int) -> Publication:
    repo = PublicationRepository(session)
    pub = await repo.create(title=title, content=content, author_id=author_id)
    await session.commit()
    await session.refresh(pub)
    return pub


async def service_update_publication(
    session: AsyncSession,
    pub_id: int,
    fields: dict,
) -> Optional[Publication]:
    repo = PublicationRepository(session)
    pub = await repo.update(pub_id, **fields)
    await session.commit()
    await session.refresh(pub)
    return pub


async def service_delete_publication(
    session: AsyncSession,
    pub_id: int,
):
    repo = PublicationRepository(session)
    await repo.delete(pub_id)
    await session.commit()
