class TokensUtils:
    """Token managing utils."""

    _user_counter = 0
    _user_token = None
    _wrong = "sldklsdfsd"

    @classmethod
    def get_token(cls, is_admin: bool = False) -> str:
        """Get token."""
        return cls._user_token

    @classmethod
    def set_token(cls, string: str, is_admin: bool = False) -> None:
        """Set token."""

        token_string = None
        s1 = string.find("=")
        s2 = string.find(";")
        token_string = string[s1 + 1 : s2]

        if cls._user_counter < 1:
            cls._user_counter += 1
            cls._user_token = token_string

    @classmethod
    def reset_user_counter(cls):
        cls._user_counter = 0


def get_user_cookies(wrong=False):
    """Get user's cookies."""
    if wrong:
        return {"users_access_token": TokensUtils._wrong}
    cookies = {"users_access_token": TokensUtils.get_token()}
    return cookies
