from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from schemas.auth import AuthData
from schemas.user import UserAdminView, UserCreate, UserListAdminView
from services.access import is_admin
from services.auth import AuthService, get_auth_service
from services.pagination import PaginationParams
from services.users import UsersService, get_users_service

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserListAdminView],
    status_code=status.HTTP_200_OK,
    summary="A list of the users",
    description="A paginated list of the users",
    response_description="The user's login, name and other information",
)
async def user_list(
    sort: str | None = Query("login"),
    pagination: PaginationParams = Depends(),
    access_data: AuthData = Security(is_admin),
    user_service: UsersService = Depends(get_users_service),
) -> list[UserListAdminView]:
    if sort is None:
        sort = "login"
    users = await user_service.get_users(sort, pagination)
    users_view = [UserListAdminView(**user.model_dump()) for user in users]
    return users_view


@router.post(
    "/",
    response_model=UserAdminView,
    status_code=status.HTTP_200_OK,
    summary="Create a user",
    description="Create a user from admin rights",
    response_description="The user's login, name and other information",
)
async def create_user(
    request: Request,
    user_create: UserCreate,
    access_data: AuthData = Security(is_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserAdminView:
    user_agent = request.state.user_agent
    user, _ = await auth_service.create_user(user_create, user_agent)
    user_view = UserAdminView(**user.model_dump())
    return user_view


@router.get(
    "/{user_id}",
    response_model=UserAdminView,
    status_code=status.HTTP_200_OK,
    summary="The user's info",
    description="All the information about the user by id",
    response_description="The user's login, name and other information",
)
async def user_by_id(
    user_id: UUID,
    access_data: AuthData = Security(is_admin),
    user_service: UsersService = Depends(get_users_service),
) -> UserAdminView:
    user = await user_service.get_user_by_id(user_id)
    user_view = UserAdminView(**user.model_dump())
    return user_view


@router.put(
    "/{user_id}",
    response_model=UserAdminView,
    status_code=status.HTTP_200_OK,
    summary="Change user's auth data",
    description="Change user's login or / and password",
    response_description="The user's login, name and other information",
)
async def change_user_auth_data(
    user_id: UUID,
    new_login: str | None = None,
    new_password: str | None = None,
    access_data: AuthData = Security(is_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserAdminView:
    user = await auth_service.change_user_auth_data(
        user_id, new_login, new_password
    )
    user_view = UserAdminView(**user.model_dump())
    return user_view


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete the account",
    description="Delete the user's account",
    response_description="The message of success",
)
async def delete_user_account(
    user_id: UUID,
    access_data: AuthData = Security(is_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    await auth_service.delete_user_auth_data(user_id)
    return {"message": "The account was successfully deleted."}


@router.put(
    "/{user_id}/assign-role",
    response_model=UserAdminView,
    status_code=status.HTTP_200_OK,
    summary="Assign a role",
    description="Assign a role to a user",
    response_description="The user's role information",
)
async def assign_user_role(
    user_id: UUID,
    new_role: str = "subscriber",
    access_data: AuthData = Security(is_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserAdminView:
    user = await auth_service.change_user_role(user_id, new_role)
    user_view = UserAdminView(**user.model_dump())
    return user_view


@router.put(
    "/{user_id}/unassign-role",
    response_model=UserAdminView,
    status_code=status.HTTP_200_OK,
    summary="Unassign a role",
    description="Unassign a role to a user",
    response_description="The user's role information",
)
async def unassign_user_role(
    user_id: UUID,
    access_data: AuthData = Security(is_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserAdminView:
    new_role = "user"
    user = await auth_service.change_user_role(user_id, new_role)
    user_view = UserAdminView(**user.model_dump())
    return user_view
