from fastapi import APIRouter, Depends, HTTPException, Request, status

from core.logger import log
from schemas.social import SocialLogin
from schemas.user import UserView
from services.auth import AuthService, get_auth_service
from services.oauth import GoogleService, YandexService
from services.users import UsersService, get_users_service

router = APIRouter()


@router.get(
    "/{provider}/login",
    summary="Social login",
    description="Get an url for login",
    response_description="An url for login",
)
async def social_login(provider: str):
    provider = provider.lower()
    if provider == "yandex":
        service = YandexService()
    elif provider == "google":
        service = GoogleService()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="An invalid oauth service name.",
        )
    url = await service.get_url()
    return url


@router.get(
    "/{provider}/auth",
    response_model=SocialLogin,
    summary="Social auth",
    description="Get the user's profile data and an access token",
    response_description="The user's profile data and an access token",
)
async def auth(
    request: Request,
    provider: str,
    code: str,
    user_service: UsersService = Depends(get_users_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> SocialLogin:

    log.debug(f"\n{__name__} provider: \n{provider}\n")

    user_agent = request.state.user_agent

    provider = provider.lower()
    if provider == "yandex":
        service = YandexService()
    elif provider == "google":
        service = GoogleService()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="An invalid oauth service name.",
        )
    user_data = await service.auth(code)

    try:
        user = await user_service.get_user_by_login(user_data.login)
        access_token, _ = await auth_service.get_tokens(
            user.id, user.role, user_agent
        )
    except:
        user, access_token = await auth_service.create_user(
            user_data, user_agent
        )

    user_view = UserView(**user.model_dump())
    social_login_data = {
        "user": user_view,
        "access_token": access_token,
    }
    social_login = SocialLogin(**social_login_data)
    return social_login
