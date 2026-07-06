import librosa  # type: ignore
import numpy as np
import os
import soundfile as sf  # type: ignore

def extract_audio_features(audio_path, silence_threshold_db=25):
    """
    Extracts key audio features from an audio file using Librosa.
    
    Features:
        - duration_sec: Overall duration of the audio in seconds.
        - rms_energy: Root-Mean-Square energy (average speaking confidence/volume).
        - pause_ratio: Percentage of silence/non-speech intervals.
        
    Args:
        audio_path (str): Path to the audio file.
        silence_threshold_db (int): The threshold in decibels below reference to consider silence (top_db).
        
    Returns:
        dict: A dictionary containing 'duration_sec', 'rms_energy', and 'pause_ratio'.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    try:
        # Load audio using soundfile first if possible for speed, or fallback to librosa
        # We load with sr=None to keep the native sample rate
        y, sr = librosa.load(audio_path, sr=None)
        
        total_samples = len(y)
        if total_samples == 0:
            return {
                "duration_sec": 0.0,
                "rms_energy": 0.0,
                "pause_ratio": 0.0
            }
            
        # 1. Duration
        duration_sec = float(total_samples / sr)
        
        # 2. RMS Energy
        # rms returns an array of shape (1, t)
        rms = librosa.feature.rms(y=y)
        avg_rms_energy = float(np.mean(rms))
        
        # 3. Pause Ratio (using librosa.effects.split to detect non-silent intervals)
        # top_db is the threshold below reference (typically max db) for silence detection
        non_silent_intervals = librosa.effects.split(y, top_db=silence_threshold_db)
        
        non_silent_samples = 0
        for start, end in non_silent_intervals:
            non_silent_samples += (end - start)
            
        silent_samples = total_samples - non_silent_samples
        pause_ratio = float(silent_samples / total_samples)
        
        # Clamp pause_ratio between 0.0 and 1.0
        pause_ratio = max(0.0, min(1.0, pause_ratio))
        
        return {
            "duration_sec": duration_sec,
            "rms_energy": avg_rms_energy,
            "pause_ratio": pause_ratio
        }
    except Exception as e:
        print(f"Error extracting audio features: {e}")
        raise e
