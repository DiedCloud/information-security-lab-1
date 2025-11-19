from typing import Optional, Any, Annotated

from fastapi import Depends
from sqlalchemy import select, update, delete, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC

from src.common.di_container import di
from src.integration.repository.entity import Publication


class PublicationRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(di.get_pg_session)]):
        self.session = session

    async def create(self, title: str, content: str, author_id: int) -> Publication:
        pub = Publication(title=title, content=content, author_id=author_id)
        self.session.add(pub)
        return pub

    async def get_by_id(self, pub_id: int) -> Optional[Publication]:
        return await self.session.get(Publication, pub_id)

    async def list(self, limit: int = 50, offset: int = 0) -> Sequence[Publication]:
        q = select(Publication).order_by(Publication.created_at.desc()).limit(limit).offset(offset)
        res = await self.session.execute(q)
        return res.scalars().all()

    async def list_by_author(self, author_id: int, limit: int = 50, offset: int = 0) -> Sequence[Publication]:
        q = (
            select(Publication)
            .where(Publication.author_id == author_id)
            .order_by(Publication.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(q)
        return res.scalars().all()

    async def update(self, pub_id: int, **fields: Any) -> Optional[Publication]:
        if not fields:
            return await self.get_by_id(pub_id)

        # обновим updated_at вручную, чтобы гарантировать изменение (если вы не полагаетесь на server_onupdate)
        fields["updated_at"] = datetime.now(UTC)

        q = (
            update(Publication)
            .where(Publication.id == pub_id)
            .values(**fields)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(q)
        return await self.get_by_id(pub_id)

    async def delete(self, pub_id: int) -> bool:
        q = delete(Publication).where(Publication.id == pub_id)
        res = await self.session.execute(q)
        return True
