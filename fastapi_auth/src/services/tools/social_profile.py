from schemas.social import ProfileGoogle, ProfileYandex
from schemas.user import UserCreate


def profile_to_user(profile_data: dict) -> UserCreate:
    """Transforms profile data to UserCreate."""

    user_dict = {}
    for key, value in profile_data.items():
        match key:
            case "email" | "default_email":
                key = "login"
                value = value
            case "first_name" | "given_name":
                key = "first_name"
                value = value
            case "last_name" | "family_name":
                key = "last_name"
                value = value
        user_dict.update({key: value})
    user_dict.update({"password": "password"})
    user = UserCreate(**user_dict)
    return user
