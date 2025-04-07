import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.claim import ClaimCreate, ClaimInDB, ClaimStatusResponse, ClaimUpdate
from app.services.claim import (
    create_claim,
    delete_claim,
    get_claim,
    get_claim_status,
    update_claim,
)

router = APIRouter()


@router.post("/claims", response_model=ClaimInDB, status_code=status.HTTP_201_CREATED)
async def submit_claim(
    claim_in: ClaimCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_claim(db, claim_in, current_user.id)


@router.get("/claims/{claim_id}", response_model=ClaimInDB)
async def fetch_claim(
    claim_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = await get_claim(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found"
        )
    return claim


@router.get("/claims/status/{claim_id}", response_model=ClaimStatusResponse)
async def fetch_claim_status(
    claim_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = await get_claim_status(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found"
        )
    return claim


@router.put("/claims/{claim_id}", response_model=ClaimInDB)
async def update_claim_endpoint(
    claim_id: uuid.UUID,
    claim_in: ClaimUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_claim = await update_claim(db, claim_id, claim_in, current_user.id)
    if not updated_claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found"
        )
    return updated_claim


@router.delete("/claims/{claim_id}")
async def delete_claim_endpoint(
    claim_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_claim(db, claim_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found"
        )
    return {"message": "Claim deleted successfully"}
