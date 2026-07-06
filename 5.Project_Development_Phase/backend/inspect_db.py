import sys
import os
from database import get_db, EvaluationResult, Transcript, AudioFeature, AudioFile

def inspect():
    with get_db() as db:
        evals = db.query(EvaluationResult).order_by(EvaluationResult.created_at.desc()).all()
        if not evals:
            print("No evaluations found in database.")
            return
            
        print(f"Found {len(evals)} evaluations:")
        for e in evals:
            print(f"\n--- Evaluation ID: {e.id} ---")
            print(f"Created At: {e.created_at}")
            print(f"Overall Score: {e.overall_score}")
            print(f"Category: {e.category}")
            print(f"Semantic Similarity Score: {e.semantic_similarity_score}")
            print(f"Filler Word Penalty: {e.filler_word_penalty}")
            print(f"Audio Features Score (Pause Penalty): {e.audio_features_score}")
            
            # Find transcript
            t = db.query(Transcript).filter_by(audio_file_id=e.audio_file_id).first()
            if t:
                print(f"Transcript Text: '{t.transcript_text}'")
                print(f"Word Count: {t.word_count}")
            else:
                print("Transcript: Not found")
                
            # Find audio features
            af = db.query(AudioFeature).filter_by(audio_file_id=e.audio_file_id).first()
            if af:
                print(f"Pause Ratio: {af.pause_ratio}")
                print(f"RMS Energy: {af.rms_energy}")
                print(f"Duration: {af.duration_sec}")
            else:
                print("Audio Features: Not found")

if __name__ == "__main__":
    inspect()
