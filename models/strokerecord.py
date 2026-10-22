from datetime import datetime
from typing import TYPE_CHECKING, Optional
from db.base import Base

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class StrokeRecord(Base):
    __tablename__ = "stroke_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # user_id disetel nullable=True untuk mengakomodasi pencatatan tamu (guest)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    encrypted_payload: Mapped[str] = mapped_column(Text, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relasi many-to-one ke User
    user: Mapped[Optional["User"]] = relationship(back_populates="records")

    def __repr__(self) -> str:
        return f"<StrokeRecord id={self.id} user_id={self.user_id} risk={self.risk_score}>"
