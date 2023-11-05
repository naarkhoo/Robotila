"""Utility functions for the app."""
from io import BytesIO

from google.cloud import texttospeech


def response_to_audio(
    response: str,
    voice: texttospeech.VoiceSelectionParams,
    audio_config: texttospeech.AudioConfig,
    client_tts: texttospeech.TextToSpeechClient,
) -> BytesIO:
    """Transcribe chatbot response to audio."""
    synthesis_input = texttospeech.SynthesisInput(text=response)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response_tts = client_tts.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Instead of saving the file, keep the audio in memory
    audio_file = BytesIO(response_tts.audio_content)
    return audio_file


def prepare_tts() -> tuple:
    """Load requirement for TTS."""
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-IN",
        # ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        name="en-IN-Neural2-A",
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    return voice, audio_config
