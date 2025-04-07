from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    db_user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None

    return user


async def generate_tokens(user_id: str) -> Tuple[str, str]:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return access_token, refresh_token


async def refresh_access_token(refresh_token: str) -> str:
    try:
        user_id = decode_refresh_token(refresh_token)
        return create_access_token(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
