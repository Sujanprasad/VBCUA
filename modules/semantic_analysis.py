import re
from sentence_transformers import SentenceTransformer, util  # type: ignore
import streamlit as st
import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()

DEFAULT_SBERT_MODEL = os.getenv("SBERT_MODEL_NAME", "all-MiniLM-L6-v2")

@st.cache_resource
def get_sentence_transformer(model_name=None):
    """
    Loads and caches the Sentence-BERT model using Streamlit's resource cache.
    """
    if model_name is None:
        model_name = DEFAULT_SBERT_MODEL
    print(f"Loading Sentence-BERT model '{model_name}'...")
    return SentenceTransformer(model_name)


def compute_semantic_similarity(transcript_text, concept_text, model_name=None):
    """
    Computes the cosine similarity between the transcript and reference concept.
    
    Args:
        transcript_text (str): Transcribed text.
        concept_text (str): Reference concept text.
        model_name (str): Sentence-BERT model name.
        
    Returns:
        float: Similarity score between 0.0 and 1.0 (clamped).
    """
    if not transcript_text.strip() or not concept_text.strip():
        return 0.0
        
    try:
        model = get_sentence_transformer(model_name)
        embeddings1 = model.encode(transcript_text, convert_to_tensor=True)
        embeddings2 = model.encode(concept_text, convert_to_tensor=True)
        similarity = util.cos_sim(embeddings1, embeddings2).item()
        
        # Clamp similarity between -1 and 1, then scale if needed, or keep cosine similarity
        return max(0.0, min(1.0, similarity))
    except Exception as e:
        print(f"Error computing semantic similarity: {e}")
        raise e

def analyze_filler_words(text):
    """
    Scans the text for common filler words using regex word boundaries.
    
    Args:
        text (str): The transcript text.
        
    Returns:
        dict: A dictionary containing:
            - 'filler_word_count': Total number of filler words.
            - 'filler_ratio': Ratio of filler words to total words.
            - 'filler_details': Dictionary showing counts for each individual filler word/phrase.
    """
    fillers = ["um", "uh", "like", "ah", "eh", "so", "actually", "basically", "you know"]
    text_lower = text.lower()
    
    # Calculate total word count
    words = text_lower.split()
    total_words = len(words)
    
    if total_words == 0:
        return {
            "filler_word_count": 0,
            "filler_ratio": 0.0,
            "filler_details": {f: 0 for f in fillers}
        }
        
    filler_details = {}
    total_fillers = 0
    
    for filler in fillers:
        # Create regex for exact word match
        if " " in filler:
            pattern = rf"\b{re.escape(filler)}\b"
        else:
            pattern = rf"\b{re.escape(filler)}\b"
            
        matches = re.findall(pattern, text_lower)
        count = len(matches)
        filler_details[filler] = count
        total_fillers += count
        
    filler_ratio = total_fillers / total_words
    
    return {
        "filler_word_count": total_fillers,
        "filler_ratio": float(filler_ratio),
        "filler_details": filler_details
    }
