import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.claim import Claim, ClaimStatus
from app.schemas.claim import ClaimCreate, ClaimUpdate


async def create_claim(
    db: AsyncSession, claim_in: ClaimCreate, user_id: uuid.UUID
) -> Claim:
    db_claim = Claim(
        user_id=user_id,
        patient_id=claim_in.patient_id,
        provider_id=claim_in.provider_id,
        service_date=claim_in.service_date,
        procedures=[proc.dict() for proc in claim_in.procedures],
        total_amount=claim_in.total_amount,
        notes=claim_in.notes,
        status=ClaimStatus.SUBMITTED,
    )
    db.add(db_claim)
    await db.commit()
    await db.refresh(db_claim)
    return db_claim


async def get_claim(
    db: AsyncSession, claim_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[Claim]:
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id, Claim.user_id == user_id)
    )
    return result.scalars().first()


async def get_claim_status(
    db: AsyncSession, claim_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[Claim]:
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id, Claim.user_id == user_id)
    )
    return result.scalars().first()


async def update_claim(
    db: AsyncSession, claim_id: uuid.UUID, claim_in: ClaimUpdate, user_id: uuid.UUID
) -> Optional[Claim]:
    claim = await get_claim(db, claim_id, user_id)
    if not claim:
        return None

    update_data = claim_in.dict(exclude_unset=True)

    if "procedures" in update_data and update_data["procedures"]:
        # Check if procedures are already dictionaries or objects with dict method
        if hasattr(update_data["procedures"][0], "dict"):
            update_data["procedures"] = [
                proc.dict() for proc in update_data["procedures"]
            ]

    for field, value in update_data.items():
        setattr(claim, field, value)

    await db.commit()
    await db.refresh(claim)
    return claim


async def delete_claim(
    db: AsyncSession, claim_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    claim = await get_claim(db, claim_id, user_id)
    if not claim:
        return False

    await db.delete(claim)
    await db.commit()
    return True


async def get_user_claims(db: AsyncSession, user_id: uuid.UUID) -> List[Claim]:
    result = await db.execute(select(Claim).where(Claim.user_id == user_id))
    return result.scalars().all()
