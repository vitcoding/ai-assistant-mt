from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from services.security.auth import login_access_token

router = APIRouter()


@router.post(
    "/auth/login",
    response_model=dict,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    token_response = await login_access_token(
        form_data.username, form_data.password
    )
    return token_response
