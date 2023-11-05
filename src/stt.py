"""Transcribe speech from an audio file stored in GCS."""
import os

import pyaudio
from google.cloud import speech

# set GOOGLE_APPLICATION_CREDENTIALS to service account key jsonfile
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds/google_stt_creds.json"
audio_local = False
microphone = True


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


def run_quickstart() -> speech.RecognizeResponse:
    """Sample code to transcribe an audio file."""
    client = speech.SpeechClient()

    if audio_local:
        # The name of the audio file to transcribe
        gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

        audio = speech.RecognitionAudio(uri=gcs_uri)

    if microphone:
        # Gets input from the microphone.
        audio = get_microphone_input()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    if len(audio) == 0:
        print("No audio data was recorded.")
    else:
        response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")


if __name__ == "__main__":
    run_quickstart()
