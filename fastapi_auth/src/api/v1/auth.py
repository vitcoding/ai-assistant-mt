from fastapi import APIRouter, Depends, Request, Response, Security, status

from schemas.user import UserCreate, UserLogin, UserView
from services.access import get_current_user
from services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserView,
    status_code=status.HTTP_201_CREATED,
    summary="Signup",
    description="Create user's auth data, set cookie",
    response_description="The user's login, name and other information",
)
async def create_user(
    request: Request,
    response: Response,
    user_create: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserView:
    user_agent = request.state.user_agent
    user, access_token = await auth_service.create_user(
        user_create, user_agent
    )
    response.set_cookie(
        key="users_access_token", value=access_token, httponly=True
    )
    user_view = UserView(**user.model_dump())
    return user_view


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Authenticate user, set cookie",
    response_description="The message of success",
)
async def login_user(
    request: Request,
    response: Response,
    user_login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    user_agent = request.state.user_agent
    access_token, _ = await auth_service.authenticate_user(
        user_login_data.login, user_login_data.password, user_agent
    )
    response.set_cookie(
        key="users_access_token", value=access_token, httponly=True
    )
    return {"message": "Login done."}


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    summary="Refresh token",
    description="Update an access and a refresh token, set cookie",
    response_description="The message of success",
)
async def token_refresh(
    auth_data: str = Security(get_current_user),
) -> dict:
    return {"message": "The tokens have been refreshed."}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout user, delete cookie",
    response_description="The message of success",
)
async def logout(
    response: Response,
    auth_data: str = Security(get_current_user),
) -> dict:
    response.delete_cookie(key="users_access_token")
    return {"message": "Logout done."}
