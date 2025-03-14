from services.tools.time_stamp import TimeStamp


def get_message_header(language: str, role: str) -> str:
    """Gets the message header."""

    timestamp = TimeStamp(language)
    time_str = timestamp.get_str_timestamp("message")
    message_header = f"[{time_str}] {role}:"
    return message_header
