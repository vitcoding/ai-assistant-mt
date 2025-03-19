from typing import Any

import numpy as np
from pydub import AudioSegment
from torch import Tensor

MAX_INT16_VALUE = 32767


class AudioEditor:
    """A class for work with audio data."""

    def save_audio(
        self,
        audio: Tensor,
        file_path: str,
        sample_rate: int = 24000,
        file_format: str = "wav",
    ) -> None:
        """Saves the audio file from Tensor."""

        audio_segment = self.tensor_to_sound(audio, sample_rate)
        audio_segment.export(file_path, format=file_format)

    def save_audio_from_tensors(
        self,
        tensors: list | tuple[Tensor],
        file_path: str,
        sample_rate: int = 24000,
        file_format: str = "wav",
    ):
        """Saves the audio file from Tensors."""

        combined_sound = None

        for audio in tensors:
            sound = self.tensor_to_sound(audio, sample_rate)
            if combined_sound is None:
                combined_sound = sound
            else:
                combined_sound += sound

        if combined_sound:
            combined_sound.export(file_path, format=file_format)

    def tensor_to_sound(
        self,
        audio: Tensor,
        sample_rate: int = 24000,
    ) -> AudioSegment:
        """Converts data from Tensor to AudioSegment."""

        audio = audio.numpy()
        audio *= MAX_INT16_VALUE / np.max(np.abs(audio))
        audio = audio.astype(np.int16)

        audio_segment = AudioSegment(
            data=bytes(audio),
            sample_width=audio.itemsize,
            frame_rate=sample_rate,
            channels=1,
        )
        return audio_segment

    def merge_wav_files(self, output_file, *input_files):
        """Combines audio files into a single file."""

        combined_sound = None

        for filename in input_files:
            sound = AudioSegment.from_wav(filename)
            if combined_sound is None:
                combined_sound = sound
            else:
                combined_sound += sound

        if combined_sound:
            combined_sound.export(output_file, format="wav")
