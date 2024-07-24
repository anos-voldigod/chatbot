import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

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
        response = chat.send_message(prompt)
        return response
    except Exception as e:
        st.error(f"Failed to get response from Gemini: {e}")
        return None

#st.set_page_config(page_title='Chatbot Evaluation')

st.header("Gemini LLM Application")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

user_input = st.text_input("Input: ", key='input_text')
submit = st.button("Enter the prompt")

if submit and user_input:
    response = get_gemini_response(user_input)
    if response:
       
        st.session_state.chat_history.append(("You", user_input))
        st.subheader("The Response is : ")
        if isinstance(response, list):
            for chunk in response:
                st.write(chunk.text)
                st.session_state.chat_history.append(("Bot", chunk.text))
        else:
            st.write(response.text)
            st.session_state.chat_history.append(("Bot", response.text))
    else:
        st.error("Failed to get a response from the model.")


st.subheader("Chat History")
for sender, message in st.session_state.chat_history:
    st.write(f"{sender}: {message}")

st.warning("To view this Streamlit app on a browser, run it with the following command:\n\n    streamlit run Chatbot.py [ARGUMENTS]")
