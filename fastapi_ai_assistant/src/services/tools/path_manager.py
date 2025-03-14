import os
from pathlib import Path

from core.logger import log


class PathManager:
    """A class for work with file / directory path."""

    def __init__(self) -> None:
        self.base_dir = "app_data/chats/"

        self.chat_id = None
        self.user_id = None
        self.chat_time = None
        self.chat_dir_audio = None
        self.chat_dir_messages = None

    def set_chat_directories(self, chat_id: str):
        """Creates chat directories."""

        self.chat_id = chat_id
        self.user_id, self.chat_time = chat_id.split("_")

        self.chat_dir_audio = (
            f"{self.base_dir}{self.user_id}/{self.chat_time}/audio/"
        )
        self.check_directory_path(self.chat_dir_audio)

        self.chat_dir_messages = (
            f"{self.base_dir}{self.user_id}/{self.chat_time}/messages/"
        )
        self.check_directory_path(self.chat_dir_messages)

    def parse_audio_message_filename(self, audio_file_name):
        """Parses an audio message file name."""

        file_name = audio_file_name.split(".")[0]
        user_id, chat_time, message_time = file_name.split("_")
        chat_id = f"{user_id}_{chat_time}"

        self.set_chat_directories(chat_id)

        new_file_name = (
            message_time.replace("-", "")
            .replace("T", "-")
            .replace("MS", "-")
            .replace("Z", "")
        )
        return new_file_name

    def check_directory_path(self, directory_path: str):
        """Checks a directory path."""

        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)

    def check_file_path(self, file_path: str):
        """Checks a file path."""

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get_latest_file_in_directory(self, directory_path):
        """Gets the latest file from the directory."""

        files = Path(directory_path).glob("*.*")
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        log.debug(
            f"{__name__}: {self.get_latest_file_in_directory.__name__}: "
            f"\nlatest_file: {latest_file}"
        )
        return latest_file
