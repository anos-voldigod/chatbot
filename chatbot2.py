import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from gtts import gTTS
import base64
import fitz  
import wave
import pyaudio
import speech_recognition as sr

load_dotenv()

st.set_page_config(
    page_title='Chatbot',
    page_icon='🤖',
    layout='centered',
    initial_sidebar_state='auto'
)

st.markdown(
    """
    <style>
    .user-avatar { width: 50px; height: 50px; border-radius: 50%; }
    .bot-avatar { width: 50px; height: 50px; border-radius: 50%; }
    </style>
    """,
    unsafe_allow_html=True
)

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")

try:
    model = genai.GenerativeModel("gemini-1.5-pro")
    chat = model.start_chat(history=[])
except Exception as e:
    st.error(f"Failed to initialize the generative model: {e}")

def get_gemini_response(prompt):
    try:
        with st.spinner("Getting response..."):
            response = chat.send_message(prompt)
        return response
    except Exception as e:
        st.error(f"Failed to get response from Gemini: {e}")
        return None

def text_to_speech(message):
    tts = gTTS(message)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        b64_audio = base64.b64encode(audio_bytes).decode()
    audio_link = f'<audio controls><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>'
    return audio_link

def extract_text_from_pdf(uploaded_file):
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()
    pdf_document.close()
    return text

def summarize_text(text):
    return "This is a mock summary of the provided text."

def voice_to_text(audio_file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand the audio.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def record_audio(filename):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []

    st.write("Recording...")
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    st.write("Recording finished.")

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

st.header("Made In Heaven 🤖")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

user_input = st.text_input("Type your message here...", key='input_text')
submit = st.button("Send")

if submit and user_input:
    response = get_gemini_response(user_input)
    if response:
        tts_audio_link = text_to_speech(response.text)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response.text, tts_audio_link))
    else:
        st.error("Failed to get a response from the model.")

if st.button("Record Voice"):
    audio_file = record_audio("output.wav")
    voice_text = voice_to_text(audio_file)
    if voice_text:
        response = get_gemini_response(voice_text)
        if response:
            tts_audio_link = text_to_speech(response.text)
            st.session_state.chat_history.append(("You (Voice)", voice_text))
            st.session_state.chat_history.append(("Bot", response.text, tts_audio_link))

st.subheader("Chat History")
for sender, message, *tts_audio_link in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"![User Avatar](user_avatar_url) You: {message}")
    elif sender == "You (Voice)":
        st.markdown(f"![User Avatar](user_avatar_url) You (Voice): {message}")
    else:
        st.markdown(f"![Bot Avatar](bot_avatar_url) Bot: {message}")
        if tts_audio_link:
            st.markdown(tts_audio_link[0], unsafe_allow_html=True)

if st.button("Clear Chat History"):
    st.session_state.chat_history = []

st.sidebar.subheader("Usage Analytics")
st.sidebar.write(f"Total Messages: {len(st.session_state.chat_history)}")

st.sidebar.subheader("Feedback")
feedback = st.sidebar.text_area("Your Feedback", placeholder="Provide your feedback here...")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")

st.sidebar.subheader("Help")
st.sidebar.write("""
    How to use this chatbot:
    - Type your message in the input box and click "Send".
    - Use the "Record Voice" button to ask questions using your voice.
    - View the chat history on the main page.
""")

pdf_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
if pdf_file:
    pdf_text = extract_text_from_pdf(pdf_file)
    st.sidebar.write("PDF uploaded successfully. Click the button below to summarize it.")
    
    if st.sidebar.button("Summarize PDF"):
        summary = summarize_text(pdf_text)
        st.sidebar.write("Summary:")
        st.sidebar.write(summary)
