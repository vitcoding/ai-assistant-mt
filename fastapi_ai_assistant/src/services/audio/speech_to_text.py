import faster_whisper
from faster_whisper import WhisperModel

from core.logger import log


class SpeechToText:
    """A class for work with the stt model."""

    def __init__(self, model_size: str = "small") -> None:
        self.model_size = model_size
        self.model = WhisperModel(
            self.model_size, device="cpu", compute_type="int8"
        )

    def get_available_models(self) -> list[str]:
        """Gets available models names."""
        available_models = faster_whisper.available_models()
        return available_models

    async def transcribe_audio(
        self, file_path: str = "recorded-audio.wav"
    ) -> str:
        """Transcribes an audio file."""

        log.info(
            f"{__name__}: {self.transcribe_audio.__name__}: Model started"
        )
        segments, info = self.model.transcribe(file_path, beam_size=5)
        log.info(
            f"{__name__}: {self.transcribe_audio.__name__}: Model finished"
        )

        log.info(
            f"{__name__}: {self.transcribe_audio.__name__}: "
            f"\nDetected language '{info.language}' "
            f"with probability {info.language_probability}"
        )
        if info.language == "nn":
            return "   "

        segments_data = [segment for segment in segments]
        chunks = [segment.text for segment in segments_data]
        text = " ".join(chunks)

        text_segments = "\n".join(
            [
                f"[{segment.start} s -> {segment.end} s] {segment.text}"
                for segment in segments_data
            ]
        )
        log.debug(
            f"{__name__}: {self.transcribe_audio.__name__}: text_segments:"
            f"\n{text_segments}"
        )

        return text
