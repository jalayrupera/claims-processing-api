import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ClaimStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"


class Claim(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    patient_id = Column(String, nullable=False)
    provider_id = Column(String, nullable=False)
    service_date = Column(DateTime(timezone=True), nullable=False)
    procedures = Column(JSONB, nullable=False)
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.SUBMITTED, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", backref="claims")
