"""Here is the main chatbot."""
import os
from typing import Optional

import streamlit as st
from audiorecorder import audiorecorder
from google.cloud import speech, texttospeech
from langchain.chains import LLMChain

# from langchain.llms import ChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from langdetect import detect
from pydub import AudioSegment
from utils import (
    audio_to_text,
    create_autoplay_audio_player,
    prepare_tts,
    response_to_audio,
)

# Set the environment variable in your code (not recommended for production)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds/text-to-speech-key.json"

# whether to print out debug messages
verbose = False

# Instantiates a client
client_tts = texttospeech.TextToSpeechClient()
voice_en, voice_da, audio_config = prepare_tts()

client_stt = speech.SpeechClient()
stt_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
    alternative_language_codes=["da-DK", "fa-IR"],
)


st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="📖")
st.title("📖 StreamlitChatMessageHistory")

# Set an OpenAI API Key before continuing
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(chat_memory=msgs)
if len(msgs.messages) == 0:
    response = (
        "Hej min ven. Robotila er her. Du kan tale med mig på dansk eller engelsk;"
    )
    # "Hello, Robotila is here; You can talk to me in Danish or English;"
    msgs.add_ai_message(response)

    lang = detect(response)
    if lang == "en":
        voice = voice_en
    else:
        voice = voice_da

    audio_file = response_to_audio(response, voice, audio_config, client_tts)

    # Create the audio player HTML with autoplay
    audio_html = create_autoplay_audio_player(audio_file)

    # Display an audio player widget to play the response in the browser
    st.markdown(audio_html, unsafe_allow_html=True)

# Set up the LLMChain, passing in memory
template = """
You are an AI chatbot called Robotila, having a conversation with 4 years old girl.
Answer her questions and ask her questions too. Try to be curious, engaging and fun.
Keep your style simple and friendly. If the message is in other language than Englush,
please answer in the same language. If questions are not clear, ask for clarification.
{history}
Human: {human_input}
AI: """
prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
llm_chain = LLMChain(
    llm=ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo"),
    prompt=prompt,
    memory=memory,
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)


# Function to handle the conversation
def handle_conversation(audio: Optional[AudioSegment]) -> None:
    """The main conversation takes place here."""
    if (audio is not None) and (audio.duration_seconds > 1):
        if verbose:
            # To get audio properties, use pydub AudioSegment properties:
            st.write(
                f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds"  # noqa: E501
            )

        # Convert audio to text
        audio_input = {
            "content": audio.raw_data,
        }

        prompt = audio_to_text(audio_input, client_stt, stt_config)

        # Display the transcribed text
        st.write(prompt)

        if verbose:
            # Display the transcribed text
            st.write("You said: " + prompt)

        # Generate the response using LLMChain
        response = llm_chain.run(prompt)

        # Display the AI's response as text
        st.chat_message("ai").write(response)

        lang = detect(response)
        if lang == "en":
            voice = voice_en
        else:
            voice = voice_da

        # Synthesize speech for the AI's response
        audio_file = response_to_audio(response, voice, audio_config, client_tts)

        # Create the audio player HTML with autoplay
        audio_html = create_autoplay_audio_player(audio_file)

        # Display an audio player widget to play the response in the browser
        # st.audio(audio_file.getvalue(), format="audio/mp3")
        st.markdown(audio_html, unsafe_allow_html=True)


# Check for audio input
audio_input = audiorecorder("Click to record", "Click to stop recording")

# Call the function to handle the conversation whenever there's audio input
if audio_input is not None and len(audio_input) > 0:
    audio_input = audio_input.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    handle_conversation(audio_input)


# # View the message contents in session state
# view_messages = st.expander("View the message contents in session state")
# with view_messages:
#     view_messages.json(st.session_state.langchain_messages)
