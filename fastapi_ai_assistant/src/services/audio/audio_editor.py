from typing import Any

import numpy as np
from pydub import AudioSegment
from torch import Tensor


class AudioEditor:

    def save_audio(
        self,
        audio: Tensor,
        file_path: str,
        sample_rate: int = 24000,
        file_format: str = "wav",
    ) -> None:
        """Saves the audio file."""

        audio = audio.numpy()
        audio *= 32767 / np.max(np.abs(audio))
        audio = audio.astype(np.int16)

        audio_segment = AudioSegment(
            data=bytes(audio),
            sample_width=audio.itemsize,
            frame_rate=sample_rate,
            channels=1,
        )

        audio_segment.export(file_path, format=file_format)

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
