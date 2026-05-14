"""Routeur principal : agrège tous les sous-routeurs v1."""

from fastapi import APIRouter

from api.v1 import auth, users

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(users.router)
