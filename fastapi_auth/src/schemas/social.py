from pydantic import BaseModel
from schemas.user import UserView


class ProfileYandex(BaseModel):
    default_email: str
    first_name: str
    last_name: str


class ProfileGoogle(BaseModel):
    email: str
    given_name: str
    family_name: str


class SocialLogin(BaseModel):
    user: UserView
    access_token: str
