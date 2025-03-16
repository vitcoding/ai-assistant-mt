import os
import re

import torch
from num2words import num2words
from transliterate import translit

from core.logger import log
from services.audio.audio_editor import AudioEditor


class TextToSpeechRu:
    """A class for work with the Russian tts model."""

    def __init__(self) -> None:
        device = torch.device("cpu")
        torch.set_num_threads(4)
        local_file = "app_data/neural_model/ru_voices_model.pt"
        if not os.path.isfile(local_file):
            torch.hub.download_url_to_file(
                "https://models.silero.ai/models/tts/ru/v3_1_ru.pt", local_file
            )
        self.__model = torch.package.PackageImporter(local_file).load_pickle(
            "tts_models", "model"
        )
        self.__model.to(device)
        self.audio_editor = AudioEditor()

    def text_to_audio(
        self,
        text: str,
        file_path: str,
        speaker: str = "xenia",
        sample_rate: int = 24000,
    ) -> None:
        """Converts text to audio by pre-splitting the text into parts."""

        text_list = text.split("\n\n")
        log.info(
            f"{__name__}: {self.generate_audio_from_text.__name__}: "
            f"\ntext_list: {text_list}"
        )
        audio_list = [
            self.generate_audio_from_text(chunk, speaker, sample_rate)
            for chunk in text_list
        ]

        self.audio_editor.save_audio_from_tensors(audio_list, file_path)

    @staticmethod
    def __num2words_ru(match: str) -> str:
        """Converts numbers into words."""
        clean_number = match.group().replace(",", ".")
        return num2words(clean_number, lang="ru")

    # Speakers available: aidar, baya, kseniya, xenia, eugene, random
    def generate_audio_from_text(
        self,
        text: str,
        speaker: str,
        sample_rate: int,
    ) -> torch.Tensor:
        """Converts text to audio."""

        words = translit(text, "ru")
        words = re.sub(r"-?[0-9][0-9,._]*", self.__num2words_ru, words)
        log.debug(
            f"{__name__}: {self.generate_audio_from_text.__name__}: "
            f"\nText after translit and num2words: {words}"
        )

        text_to_speak = f"{' '*5}{words}"
        if sample_rate not in [48000, 24000, 8000]:
            sample_rate = 24000
        if speaker not in [
            "aidar",
            "baya",
            "kseniya",
            "xenia",
            "eugene",
            "random",
        ]:
            speaker = "xenia"

        log.info(
            f"{__name__}: {self.generate_audio_from_text.__name__}: Model started"
        )

        try:
            audio = self.__model.apply_tts(
                text=text_to_speak,
                speaker=speaker,
                sample_rate=sample_rate,
            )
        except ValueError as err:
            log.error(
                f"{__name__}: {self.generate_audio_from_text.__name__}: "
                f"\nBad input: Error: {err}"
            )
            return None

        log.info(
            f"{__name__}: {self.generate_audio_from_text.__name__}: Model finished"
        )
        return audio
