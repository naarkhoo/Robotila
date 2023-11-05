"""Main streamlit app."""
import os

import pyaudio
import streamlit as st
from audiorecorder import audiorecorder
from google.cloud import speech

# set GOOGLE_APPLICATION_CREDENTIALS to the path for service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds/google_stt_creds.json"
client = speech.SpeechClient()
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
    alternative_language_codes=["da-DK", "fa-IR"],
)


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

    return [result.alternatives[0].transcript for result in response.results]


def main() -> None:
    """The main streamlit app."""
    st.title("Speech to Text App")

    # Create a button to record audio
    # record_button = st.button("Record")

    audio = audiorecorder("Click to record", "Click to stop recording")
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    if len(audio) > 0:
        # To play audio in frontend:
        st.audio(audio.export().read())

        # To save audio to a file, use pydub export method:
        # audio.export("audio.wav", format="wav")

        # To get audio properties, use pydub AudioSegment properties:
        st.write(
            f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds"  # noqa: E501
        )

        if audio.duration_seconds > 1:
            # Convert audio to text
            audio = {
                "content": audio.raw_data,
            }

            text = audio_to_text(audio, client, config)

            # Display the transcribed text
            st.write(text)


if __name__ == "__main__":
    main()
