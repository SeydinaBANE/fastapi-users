"""Logique métier utilisateurs (lecture, mise à jour, suppression)."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User
from repositories.user_repository import UserRepository
from schemas.user import UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def get_me(self, user: User) -> User:
        return user

    async def update_me(self, user: User, data: UserUpdate) -> User:
        if data.full_name is not None:
            user.full_name = data.full_name
        return await self._repo.update(user)

    async def get_all(self) -> list[User]:
        return await self._repo.get_all()

    async def get_by_id(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable"
            )
        return user

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.is_active is not None:
            user.is_active = data.is_active
        logger.info("Utilisateur %d mis à jour", user_id)
        return await self._repo.update(user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        logger.info("Utilisateur %d supprimé", user_id)
        await self._repo.delete(user)
