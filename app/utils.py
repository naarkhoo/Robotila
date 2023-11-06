"""Utility functions for the app."""
import base64
from io import BytesIO

import pyaudio
from google.cloud import speech, texttospeech


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

    voice = texttospeech.VoiceSelectionParams(
        language_code="da-DK",
        # ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        name="da-DK-Wavenet-A",
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.75,  # Adjust this value as needed for desired speed
    )
    return voice, audio_config


def audio_to_text(
    audio: bytes, client: speech.SpeechClient, config: speech.RecognitionConfig
) -> list:
    """Audio to text."""
    if len(audio) == 0:
        print("No audio data was recorded.")
    else:
        response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    # return [result.alternatives[0].transcript for result in response.results]
    return result.alternatives[0].transcript


def get_microphone_input() -> bytes:
    """Gets input from the microphone."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)

    frames = []
    while True:
        data = stream.read(1024)
        frames.append(data)
        if len(frames) >= 5:
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    return b"".join(frames)


# Function to create an audio player with autoplay enabled
def create_autoplay_audio_player(
    audio_file: BytesIO, file_type: str = "audio/mp3"
) -> str:
    """Create an audio player with autoplay enabled."""
    base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")
    audio_html = f"""
        <audio autoplay>
            <source src="data:{file_type};base64,{base64_audio}" type="{file_type}">
            Your browser does not support the audio element.
        </audio>
    """
    return audio_html
