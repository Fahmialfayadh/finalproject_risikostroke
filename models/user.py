from typing import TYPE_CHECKING, List, Optional
from db.base import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .strokerecord import StrokeRecord


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    public_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relasi one-to-many ke StrokeRecord
    records: Mapped[List["StrokeRecord"]] = relationship(
        "StrokeRecord", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"
