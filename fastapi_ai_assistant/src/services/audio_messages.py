from faster_whisper import WhisperModel

from core.logger import log

# import faster_whisper

# print(faster_whisper.available_models())

model_size = "small"
# model_size = "tiny"


def transcribe_file():
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe("recorded-audio.wav", beam_size=5)

    log.info(
        f"{__name__}: {transcribe_file.__name__}: "
        f"\nDetected language '{info.language}' "
        f"with probability {info.language_probability}"
    )

    chunks = [segment.text for segment in segments]
    text = " ".join(chunks)
    # for segment in segments:
    #     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    return text


async def atranscribe_file():
    """Transcribes an audio file."""

    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe("recorded-audio.wav", beam_size=5)

    log.info(
        f"{__name__}: {atranscribe_file.__name__}: "
        f"\nDetected language '{info.language}' "
        f"with probability {info.language_probability}"
    )

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
        f"{__name__}: {atranscribe_file.__name__}: text_segments:"
        f"\n{text_segments}"
    )

    return text
