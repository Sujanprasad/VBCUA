import streamlit as st
from src.speech_to_text import test_transcription

st.set_page_config(page_title="Voice Analyser", page_icon="🎙️")

st.title("🎙️ Voice-Based Concept Understanding Analyser")
st.write("Checking system integrity...")

if st.button("Test Engine Connection"):
    result = test_transcription()
    st.success(result)
else:
    st.info("Click the button to test if the module imports are working.")