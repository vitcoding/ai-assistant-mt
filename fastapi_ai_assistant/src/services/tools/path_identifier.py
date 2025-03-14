from services.tools.time_stamp import TimeStamp


class PathCreator:
    """A class for work with paths."""

    def __init__(self, timestamp: TimeStamp, user_id: str | None) -> None:
        self.timestamp = timestamp
        self.user_id = self.validate_user_id(user_id)

    def validate_user_id(self, user_id: str | None) -> str:
        """Validates an user id."""

        if user_id is None:
            user_id = "noname"
        return user_id

    def get_url(self) -> str:
        """Gets url."""
        return f"{self.user_id}_{self.timestamp.get_str_timestamp("url")}"
