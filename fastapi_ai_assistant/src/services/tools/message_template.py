from services.tools.time_stamp import TimeStamp


def get_message_header(language: str, role: str | None) -> str:
    """Gets the message header."""

    timestamp = TimeStamp(language)
    time_str = timestamp.get_str_timestamp("message")
    if role is None:
        return f"[{time_str}]:"
    return f"[{time_str}] {role}:"


def get_chat_start_message(language: str, chat_id: str):
    """Gets the chat start message."""
    if language == "Russian":
        start_message = f"Новый чат '{chat_id}' запущен."
    else:
        start_message = f"New chat '{chat_id}' has been started."
    return start_message
