"""User CRUD service (for managing the auth User model via admin endpoints)."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.security.password import hash_password
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams


class UserService(BaseService[UserRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserRepository(db), db, "users")

    async def list_users(self, pagination: PaginationParams):
        return await self.list(
            pagination,
            filters={"is_deleted": False},
            search_columns=["email", "full_name"],
        )

    async def create_user(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_email(data.get("email", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{data['email']}' already exists",
            )
        data["hashed_password"] = hash_password(data.pop("password"))
        return await self.create(data, user_id)

    async def update_user(self, record_id: str, data: dict, user_id: str | None = None):
        if "email" in data and data["email"]:
            if await self.repo.is_duplicate_email(data["email"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{data['email']}' already exists",
                )
        if "password" in data:
            data["hashed_password"] = hash_password(data.pop("password"))
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    async def delete_user(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
