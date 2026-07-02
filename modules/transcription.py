import whisper  # type: ignore
import os
import librosa  # type: ignore
import streamlit as st
from dotenv import load_dotenv  # type: ignore

load_dotenv()

DEFAULT_WHISPER_MODEL = os.getenv("WHISPER_MODEL_SIZE", "base")

@st.cache_resource
def get_whisper_model(model_name=None):
    """
    Loads and caches the Whisper model using Streamlit's resource cache.
    """
    if model_name is None:
        model_name = DEFAULT_WHISPER_MODEL
    print(f"Loading Whisper model '{model_name}'...")
    return whisper.load_model(model_name)


def transcribe_audio(audio_path, model_name=None):
    """
    Transcribes an audio file using OpenAI Whisper.
    
    Args:
        audio_path (str): Path to the audio file.
        model_name (str): Whisper model to use ('tiny', 'base', etc.).
        
    Returns:
        dict: A dictionary containing:
            - 'text': The transcription text.
            - 'word_count': The total word count.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    try:
        model = get_whisper_model(model_name)
        
        # Load audio using librosa at 16000Hz mono to bypass external ffmpeg dependency
        audio_array, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        result = model.transcribe(audio_array)
        text = result.get("text", "").strip()
        words = text.split()
        word_count = len(words)
        
        return {
            "text": text,
            "word_count": word_count
        }
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        raise e
