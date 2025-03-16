from fastapi import APIRouter, Depends, Query, Response, Security, status

from schemas.auth import AuthData
from schemas.token import RefreshTokenSession
from schemas.user import UserView
from services.access import get_current_user
from services.auth import AuthService, get_auth_service
from services.pagination import PaginationParams
from services.users import UsersService, get_users_service

router = APIRouter()


@router.get(
    "/",
    response_model=UserView,
    status_code=status.HTTP_200_OK,
    summary="The user's info",
    description="All the information about the user",
    response_description="The user's login, name and other information",
)
async def get_user(
    auth_data: AuthData = Security(get_current_user),
    users_service: UsersService = Depends(get_users_service),
) -> UserView:
    user = await users_service.get_user_by_id(auth_data.user_id)
    user_view = UserView(**user.model_dump())
    return user_view


@router.put(
    "/",
    response_model=UserView,
    status_code=status.HTTP_200_OK,
    summary="Change auth data",
    description="Change login or / and password",
    response_description="The login, name and other information",
)
async def change_user_auth_data(
    new_login: str | None = None,
    new_password: str | None = None,
    auth_data: AuthData = Security(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserView:
    user = await auth_service.change_user_auth_data(
        auth_data.user_id, new_login, new_password
    )
    user_view = UserView(**user.model_dump())
    return user_view


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Delete the account",
    description="Delete the user's account",
    response_description="The message of success",
)
async def delete_user_account(
    response: Response,
    auth_data: AuthData = Security(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    await auth_service.delete_user_auth_data(auth_data.user_id)
    response.delete_cookie(key="users_access_token")
    return {"message": "The account was successfully deleted."}


@router.get(
    "/sessions",
    response_model=list[RefreshTokenSession],
    status_code=status.HTTP_200_OK,
    summary="The user's sessions",
    description="The history of the user's sessions",
    response_description="The user's login time, user-agent",
)
async def get_user_sessions(
    sort: str | None = Query("-created_at"),
    pagination: PaginationParams = Depends(),
    auth_data: AuthData = Security(get_current_user),
    users_service: UsersService = Depends(get_users_service),
) -> list[RefreshTokenSession]:
    if sort is None:
        sort = "-created_at"
    sessions = await users_service.get_user_sessions(
        auth_data.user_id, sort, pagination
    )
    sessions_view = [
        RefreshTokenSession(**session.model_dump()) for session in sessions
    ]
    return sessions_view
