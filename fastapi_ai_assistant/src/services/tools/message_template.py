from services.tools.time_stamp import TimeStamp


def get_message_header(language: str, role: str | None) -> tuple[str]:
    """Gets the message header and the file name."""

    timestamp = TimeStamp(language)
    time_message = timestamp.get_str_timestamp("message")
    file_name = timestamp.get_str_timestamp("file")

    if role is None:
        return f"[{time_message}]:"
    return f"[{time_message}] {role}:", file_name


def get_chat_start_message(language: str, chat_id: str):
    """Gets the chat start message."""

    if language == "Russian":
        start_message = f"Новый чат '{chat_id}' запущен."
    else:
        start_message = f"New chat '{chat_id}' has been started."
    return start_message
