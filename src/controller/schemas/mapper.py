from src.controller.schemas.schemas import PublicationOut
from src.integration.repository.entity import Publication


def map_publication(pub: Publication) -> PublicationOut:
    return PublicationOut(
        id=pub.id,
        title=pub.title,
        content=pub.content,
        author_id=pub.author_id,
        created_at=pub.created_at,
        updated_at=pub.updated_at,
    )