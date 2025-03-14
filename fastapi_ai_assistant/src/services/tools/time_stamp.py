import locale
from datetime import datetime, timezone

from services.llm_languages import LANGUAGES, LOCALES


class TimeStamp:
    """A class for work with timestamp."""

    def __init__(
        self,
        languge: str | None = "English",
        timestamp: datetime | None = None,
    ):
        self.timestamp = self.validate_timestamp(timestamp)
        self.language = self.set_language(languge)

    def validate_timestamp(
        self, datetime_: datetime | None = None
    ) -> datetime:
        """Validates a timestamp."""

        timestamp = datetime_
        if datetime_ is None:
            timestamp = datetime.now(timezone.utc)
        return timestamp

    def set_language(self, language: str) -> None:
        """Sets a language."""

        if language in LANGUAGES:
            self.language = language

        locale_code = LOCALES.get(self.language)
        if locale_code is not None:
            locale.setlocale(locale.LC_ALL, locale_code)

    def get_str_timestamp(self, timestamp_format: str) -> str:
        """
        Gets a string timestamp for:
        'precisely', 'message', 'file', 'url'.
        """

        match timestamp_format:
            case "precisely":
                timestamp_formatted = self.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )
            case "message":
                timestamp_formatted = self.timestamp.strftime(
                    "%a %Y-%b-%d %H:%M:%S"
                )
            case "file" | "url":
                timestamp_formatted = self.timestamp.strftime(
                    "%Y%m%d-%H%M%S-%f"
                )
            case _:
                timestamp_formatted = self.timestamp.isoformat()
        return timestamp_formatted
