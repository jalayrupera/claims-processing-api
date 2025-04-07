from fastapi import APIRouter

from app.api.endpoints import claims, users

api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])
api_router.include_router(claims.router, tags=["claims"])
