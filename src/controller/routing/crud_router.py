from fastapi import APIRouter, Path, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.controller.routing.auth import get_current_user
from src.controller.schemas.mapper import map_publication
from src.controller.schemas.schemas import PublicationCreate, PublicationUpdate, PublicationOut, UserRead
from src.integration.repository.entity import Publication, User
from src.integration.repository.publication_repository import PublicationRepository
from src.service.crud_service import (
    service_list_publications,
    service_get_publication,
    service_create_publication,
    service_update_publication,
    service_delete_publication,
)

crud_router = APIRouter(prefix="/api/data", tags=["CRUD операции публикаций"], dependencies=[Depends(get_current_user)])


async def inject_publication_by_id(
    publication_id: int,
    publications_repo: PublicationRepository = Depends(PublicationRepository),
):
    pub = await service_get_publication(publications_repo, publication_id)
    if not pub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    return pub


async def inject_owned_publication_by_id(
    publication: Publication = Depends(inject_publication_by_id),
    user: User = Depends(get_current_user),
):
    if user.id != publication.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return publication


@crud_router.get("/", responses={status.HTTP_200_OK: {"model": list[PublicationOut]}})
async def get_data(
    limit: int = 50,
    offset: int = 0,
    publications_repo: PublicationRepository = Depends(PublicationRepository),
):
    return list(map(map_publication, await service_list_publications(publications_repo, limit, offset)))


@crud_router.get("/{publication_id}", responses={status.HTTP_200_OK: {"model": PublicationOut}})
async def get_by_id(
    publication: Publication = Depends(inject_publication_by_id),
):
    return map_publication(publication)


@crud_router.post("/", responses={status.HTTP_201_CREATED: {"model": PublicationOut}})
async def create_publication(
    payload: PublicationCreate,
    session: AsyncSession = Depends(di.get_pg_session),
    current_user: UserRead = Depends(get_current_user),
):
    return map_publication(
        await service_create_publication(
            session=session,
            title=payload.title,
            content=payload.content,
            author_id=current_user.id,
        )
    )


@crud_router.patch("/{publication_id}", responses={status.HTTP_200_OK: {"model": PublicationOut}})
async def patch_by_id(
    payload: PublicationUpdate,
    publication_id: int = Path(..., description="Id of the data"),
    owned_publication: Publication = Depends(inject_owned_publication_by_id),
    session: AsyncSession = Depends(di.get_pg_session),
):
    update_fields = payload.model_dump(exclude_unset=True)

    if not update_fields:
        return map_publication(owned_publication)

    return map_publication(await service_update_publication(session, publication_id, update_fields))


@crud_router.delete("/{publication_id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_by_id(
    publication_id: int = Path(..., description="Id of the data"),
    owned_publication: Publication = Depends(inject_owned_publication_by_id),
    session: AsyncSession = Depends(di.get_pg_session),
):
    await service_delete_publication(session, publication_id)
