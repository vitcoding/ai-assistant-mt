from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.roles import Role
from schemas.auth import AuthData
from schemas.roles import RoleCreate, RoleInDB, RoleUpdate
from services.access import is_admin
from services.roles import RolesService, get_roles_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[RoleInDB],
    status_code=status.HTTP_200_OK,
    summary="Get a list of roles",
)
async def get_roles(
    access_data: AuthData = Security(is_admin),
    roles_service: RolesService = Depends(get_roles_service),
) -> List[RoleInDB]:
    roles = await roles_service.get_roles()
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roles found in the database.",
        )

    return [RoleInDB(**jsonable_encoder(role)) for role in roles]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RoleInDB,
    summary="Create a role",
)
async def create_role(
    role_create: RoleCreate,
    access_data: AuthData = Security(is_admin),
    roles_service: RolesService = Depends(get_roles_service),
) -> RoleInDB:
    if await roles_service.get_role_by_name(role_create):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A role with name '{role_create.name}' already exists.",
        )
    try:
        new_role = await roles_service.add_role(role_create)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while inserting the role.",
        )
    return RoleInDB(**jsonable_encoder(new_role))


@router.put(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoleInDB,
    summary="Update a role",
)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    access_data: AuthData = Security(is_admin),
    roles_service: RolesService = Depends(get_roles_service),
) -> RoleInDB:
    role_to_update = await roles_service.get_role_by_id(role_id)
    if not role_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
        )
    role = await roles_service.update_role(role_to_update, role_data)
    return RoleInDB(**jsonable_encoder(role))


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete the role",
)
async def delete_role(
    role_id: UUID,
    access_data: AuthData = Security(is_admin),
    roles_service: RolesService = Depends(get_roles_service),
) -> dict:
    role_to_delete = await roles_service.get_role_by_id(role_id)
    if not role_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
        )
    try:
        await roles_service.remove_role(role_to_delete)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL, detail=str(e)
        )
    return {"message": "The role was successfully deleted."}
