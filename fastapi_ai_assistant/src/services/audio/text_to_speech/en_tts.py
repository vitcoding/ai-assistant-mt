import torch
from kokoro import KPipeline

from core.logger import log
from services.audio.audio_editor import AudioEditor


class TextToSpeechEn:
    """A class for work with the English tts model."""

    def __init__(
        self,
        voice_model_src: str = "app_data/kokoro_voices/af_nova.pt",
    ):
        self.voice_model_src = voice_model_src
        self.audio_editor = AudioEditor()

    def text_to_audio(
        self,
        text: str,
        file_path: str,
        split_pattern: str | None = r"(\n\n)+",
    ) -> None:
        """Converts text to audio."""

        log.info(f"{__name__}: {self.text_to_audio.__name__}: Model started")

        pipeline = KPipeline(lang_code="a")

        voice_tensor = torch.load(self.voice_model_src, weights_only=True)
        generator = pipeline(
            text, voice=voice_tensor, speed=1, split_pattern=split_pattern
        )

        log.info(f"{__name__}: {self.text_to_audio.__name__}: Model finished")

        tensors = []
        for i, (gs, ps, audio) in enumerate(generator):
            log.debug(
                f"{__name__}: {self.text_to_audio.__name__}: tts_data:"
                f"\nindex: {i}\ngraphemes/text: {gs}\nphonemes: {ps}"
            )
            tensors.append(audio)
            self.audio_editor.save_audio_from_tensors(tensors, file_path)
