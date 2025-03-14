from datetime import datetime, timezone


class TimeStamp:
    """A class for work with timestamp."""

    def __init__(self, timestamp: datetime | None = None):
        self.timestamp = self.validate_timestamp(timestamp)

    def validate_timestamp(
        self, datetime_: datetime | None = None
    ) -> datetime:
        """Validates a timestamp."""

        timestamp = datetime_
        if datetime_ is None:
            timestamp = datetime.now(timezone.utc)
        return timestamp

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
            case "file":
                timestamp_formatted = self.timestamp.strftime(
                    "%Y%m%d_%H%M%S_%f"
                )
            case "url":
                timestamp_formatted = self.timestamp.strftime(
                    "%Y%m%d-%H%M%S-%f"
                )
            case _:
                timestamp_formatted = self.timestamp.isoformat()
        return timestamp_formatted


if __name__ == "__main__":
    timestamp = TimeStamp()
    print(timestamp.get_str_timestamp("url"))
