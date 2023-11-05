"""here is the main chatbot."""
import os

import streamlit as st
from google.cloud import texttospeech
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from utils import prepare_tts, response_to_audio

# Set the environment variable in your code (not recommended for production)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds/text-to-speech-key.json"

# Instantiates a client
client_tts = texttospeech.TextToSpeechClient()
voice, audio_config = prepare_tts()

st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="📖")
st.title("📖 StreamlitChatMessageHistory")

"""
A basic example of using StreamlitChatMessageHistory to help LLMChain remember messages in a conversation. # noqa: E501
The messages are stored in Session State across re-runs automatically. You can view the contents of Session State
in the expander below. View the
[source code for this app](https://github.com/langchain-ai/streamlit-agent/blob/main/streamlit_agent/basic_memory.py). # noqa: E501
"""


# set an OpenAI API Key before continuing

openai_api_key = os.environ.get("OPENAI_API_KEY")

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(chat_memory=msgs)
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

view_messages = st.expander("View the message contents in session state")

# Set up the LLMChain, passing in memory
template = """You are an AI chatbot having a conversation with a human.

{history}
Human: {human_input}
AI: """
prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
llm_chain = LLMChain(
    llm=OpenAI(openai_api_key=openai_api_key), prompt=prompt, memory=memory
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    response = llm_chain.run(prompt)
    st.chat_message("ai").write(response)

    audio_file = response_to_audio(response, voice, audio_config, client_tts)

    # Display an audio player widget to play the response in the browser
    st.audio(audio_file.getvalue(), format="audio/mp3")

    # # The response's audio_content is binary.
    # with open("output.mp3", "wb") as out:
    #     # Write the response to the output file.
    #     out.write(response_tts.audio_content)
    #     print('Audio content written to file "output.mp3"')


# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Memory initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    memory = ConversationBufferMemory(chat_memory=msgs)
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)
