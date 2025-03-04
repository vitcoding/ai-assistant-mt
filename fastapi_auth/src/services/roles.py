from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select

from db.postgres import get_session
from models.roles import Role
from schemas.roles import RoleCreate, RoleUpdate


class RolesService:
    """Users managing service."""

    def __init__(self, db_postgres) -> None:
        self.db_postgres = db_postgres

    async def get_roles(self) -> list:
        """Get a list of the roles."""

        query = select(Role)
        result = await self.db_postgres.execute(query)
        return result.scalars().all()

    async def get_role_by_name(self, role: RoleCreate) -> Role | None:
        """Get the role by the name."""

        existing_role = await self.db_postgres.execute(
            select(Role).where(Role.name == role.name)
        )
        if role := existing_role.first():
            return role
        return None

    async def add_role(self, role: RoleCreate) -> Role:
        """Create a role."""

        if role.description is None:
            raise ValueError("Description cannot be None.")

        new_role = Role(name=role.name, description=role.description)
        self.db_postgres.add(new_role)
        await self.db_postgres.commit()
        await self.db_postgres.refresh(new_role)
        return new_role

    async def get_role_by_id(self, role_id: UUID) -> Role:
        """Get the role by id."""

        query = select(Role).where(Role.id == role_id)
        existing_role = await self.db_postgres.execute(query)
        return existing_role.scalars().first()

    async def update_role(self, role_to_update, role_data: RoleUpdate):
        """Update the role."""

        if role_data.name:
            role_to_update.name = role_data.name
        if role_data.description:
            role_to_update.description = role_data.description

        await self.db_postgres.commit()
        await self.db_postgres.refresh(role_to_update)
        return role_to_update

    async def remove_role(self, role: RoleCreate):
        """Delete the role."""

        await self.db_postgres.delete(role)
        await self.db_postgres.commit()


@lru_cache()
def get_roles_service(
    db=Depends(get_session),
) -> RolesService:
    """RolesService provider."""
    return RolesService(db)
