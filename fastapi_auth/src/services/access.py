from fastapi import Depends, HTTPException, Request, Response, Security, status
from fastapi.encoders import jsonable_encoder

from core.logger import log
from schemas.auth import AuthData
from schemas.token import RefreshTokenInDB
from services.auth import AuthService, get_auth_service
from services.token import TokenService, get_token_service


async def get_current_user(
    request: Request,
    response: Response,
    token_service: TokenService = Depends(get_token_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthData:
    """Get current user from cookies."""

    access_token = token_service.get_access_data(
        request,
    )
    flag, auth_data_dict = token_service.check_token(
        access_token, access_data=True
    )
    if flag is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. You need to login.",
        )
    auth_data = AuthData(**auth_data_dict)
    if flag is not False:
        return auth_data

    refresh_token_db = await auth_service.get_last_refresh_token(
        auth_data.user_id
    )
    if not refresh_token_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. You need to login.",
        )
    refresh_token_schema = RefreshTokenInDB(
        **jsonable_encoder(refresh_token_db)
    )
    flag_refresh, refresh_token_check_result = token_service.check_token(
        refresh_token_schema.refresh_token
    )
    log.debug("\nrefresh_token: \n%s\n", refresh_token_db)
    log.debug("\nrefresh_token check: \n%s\n", refresh_token_check_result)
    if flag_refresh in (False, None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. You need to login",
        )

    user_agent = request.state.user_agent
    access_token, _ = await auth_service.get_tokens(
        auth_data.user_id, auth_data.user_role, user_agent
    )
    token_service.set_access_data(response, access_token)
    _, auth_data_dict = token_service.check_token(
        access_token, access_data=True
    )
    auth_data = AuthData(**auth_data_dict)
    return auth_data


async def is_admin(
    auth_data: AuthData = Security(get_current_user),
) -> AuthData:
    """Check the user's role is 'admin'."""

    if auth_data.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access is denied.",
        )
    return auth_data
