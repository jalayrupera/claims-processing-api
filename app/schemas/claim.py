import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ClaimStatusEnum(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"


class Procedure(BaseModel):
    code: str
    amount: float
    description: str = Field(..., min_length=1, max_length=500)


class ClaimBase(BaseModel):
    patient_id: str = Field(..., min_length=1)
    provider_id: str = Field(..., min_length=1)
    service_date: date
    procedures: List[Procedure]
    total_amount: float = Field(..., gt=0)
    notes: Optional[str] = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    patient_id: Optional[str] = None
    provider_id: Optional[str] = None
    service_date: Optional[date] = None
    procedures: Optional[List[Procedure]] = None
    total_amount: Optional[float] = None
    notes: Optional[str] = None
    status: Optional[ClaimStatusEnum] = None


class ClaimInDB(ClaimBase):
    id: uuid.UUID
    status: ClaimStatusEnum = ClaimStatusEnum.SUBMITTED
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClaimStatusResponse(BaseModel):
    id: uuid.UUID
    status: ClaimStatusEnum
    updated_at: datetime

    class Config:
        from_attributes = True
