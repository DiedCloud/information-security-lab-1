from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    func, Index, ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.integration.repository._base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    publications: Mapped[list["Publication"]] = relationship(
        "Publication",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id} login={self.login!r})>"

class Publication(Base):
    __tablename__ = "publications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    author: Mapped["User"] = relationship(
        "User",
        back_populates="publications",
        lazy="joined"
    )

    __table_args__ = (
        Index("ix_publications_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Publication(id={self.id} title={self.title!r} author_id={self.author_id})>"
