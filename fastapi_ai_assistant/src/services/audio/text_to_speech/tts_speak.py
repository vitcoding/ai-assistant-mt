from services.audio.text_to_speech.en_tts import TextToSpeechEn
from services.audio.text_to_speech.ru_tts import TextToSpeechRu


async def speak(
    speaker_object: TextToSpeechRu | TextToSpeechEn,
    words: str,
) -> None:
    """Calls the text-to-speech (tts) model."""

    if isinstance(speaker_object, TextToSpeechRu):
        speaker_object.text_to_audio(text=words)
    if isinstance(speaker_object, TextToSpeechEn):
        speaker_object.text_to_audio(text=words)
