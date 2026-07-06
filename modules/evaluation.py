def map_similarity_to_score(similarity):
    """
    Maps the S-BERT cosine similarity score (0.0 to 1.0) to a standard 
    academic grading scale (0 to 100).
    """
    if similarity < 0.15:
        # Completely unrelated content
        return max(0.0, similarity * 100.0)
    elif similarity < 0.40:
        # Partially related but weak content
        # Map [0.15, 0.40] to [15.0, 60.0]
        return 15.0 + (similarity - 0.15) * (45.0 / 0.25)
    elif similarity < 0.70:
        # Good paraphrased content
        # Map [0.40, 0.70] to [60.0, 90.0]
        return 60.0 + (similarity - 0.40) * (30.0 / 0.30)
    else:
        # Excellent match / near verbatim content
        # Map [0.70, 1.00] to [90.0, 100.0]
        return 90.0 + (similarity - 0.70) * (10.0 / 0.30)

def evaluate_response(semantic_score, filler_ratio, filler_word_count, pause_ratio, rms_energy, word_count):
    """
    Combines similarity, filler words, and audio characteristics to produce a final grade.
    
    Grading Rules:
        - Semantic Score Base: mapped using map_similarity_to_score
        - Filler Penalty: Deducted if filler ratio > 2%. Max penalty 20 points.
        - Pause Penalty: Deducted if pause ratio > 25% (hesitation) or < 5% (rushed). Max penalty 20 points.
        - Volume Penalty: Deducted if average RMS energy is extremely low (< 0.015), indicating whispering/low confidence.
        
    Args:
        semantic_score (float): Cosine similarity from Sentence-BERT (0.0 to 1.0).
        filler_ratio (float): Filler word count over total words.
        filler_word_count (int): Total count of filler words.
        pause_ratio (float): Ratio of silence in audio (0.0 to 1.0).
        rms_energy (float): Root-mean-square energy (average volume).
        word_count (int): Total words transcribed.
        
    Returns:
        dict: A dictionary containing:
            - 'semantic_score_base': Similarity score scaled to 100.
            - 'filler_penalty': Deduction points for filler words.
            - 'pause_penalty': Deduction points for pause spacing.
            - 'volume_penalty': Deduction points for low volume.
            - 'overall_score': Clean final score from 0 to 100.
            - 'category': "Strong", "Moderate", or "Poor".
            - 'feedback_notes': Structured text feedback listing strengths and growth areas.
    """
    # 1. Base Semantic Score
    base_score = map_similarity_to_score(semantic_score)

    
    # 2. Filler Word Penalty
    filler_penalty = 0.0
    if filler_ratio > 0.02:
        # Subtract 1.5 points for every 1% of fillers over 2%
        filler_penalty = min(20.0, (filler_ratio - 0.02) * 150.0)
        
    # 3. Pause / Pacing Penalty
    pause_penalty = 0.0
    if pause_ratio > 0.25:
        # Deduct for too much silence (hesitation)
        pause_penalty = min(20.0, (pause_ratio - 0.25) * 100.0)
    elif pause_ratio < 0.05 and word_count > 5:
        # Deduct for too little silence (speaking too fast)
        pause_penalty = 5.0
        
    # 4. Volume / RMS Penalty
    volume_penalty = 0.0
    if rms_energy < 0.012 and word_count > 0:
        volume_penalty = 8.0
    elif rms_energy < 0.020 and word_count > 0:
        volume_penalty = 4.0
        
    # Calculate Overall Score
    overall_score = base_score - filler_penalty - pause_penalty - volume_penalty
    overall_score = max(0.0, min(100.0, overall_score))
    
    # Categorization
    if overall_score >= 80.0:
        category = "Strong"
    elif overall_score >= 50.0:
        category = "Moderate"
    else:
        category = "Poor"
        
    # Generate structured feedback
    feedback = []
    
    # Content Feedback
    if semantic_score >= 0.75:
        feedback.append("✨ **Content Quality**: Excellent! Your explanation strongly aligns with the reference concept, using accurate terminology and structure.")
    elif semantic_score >= 0.50:
        feedback.append("👍 **Content Quality**: Good attempt. You covered the general concept but missed some key details or vocabulary. Try to be more specific.")
    else:
        feedback.append("❌ **Content Quality**: The semantic overlap with the reference concept is low. Review the core definition and try to address all its main parts.")
        
    # Filler Words Feedback
    if filler_penalty == 0.0:
        feedback.append("🎙️ **Speech Fluency**: Great flow! You kept filler words to a minimum.")
    elif filler_penalty < 10.0:
        feedback.append(f"⚠️ **Speech Fluency**: Moderately fluent. You used {filler_word_count} filler words ({filler_ratio:.1%}). Try practicing to reduce hesitations.")
    else:
        feedback.append(f"🛑 **Speech Fluency**: High filler usage! You used {filler_word_count} filler words ({filler_ratio:.1%}). Focus on speaking in deliberate sentences with intentional pauses.")
        
    # Pacing / Silence Feedback
    if pause_ratio > 0.35:
        feedback.append(f"⏱️ **Speech Pacing**: You have a high proportion of silence ({pause_ratio:.1%}). This suggests you might be searching for words. Try preparing an outline before speaking.")
    elif pause_ratio < 0.05 and word_count > 5:
        feedback.append("⏱️ **Speech Pacing**: You spoke very quickly with almost no pauses. Remember to take natural breaths so your explanation is easier to follow.")
    else:
        feedback.append("⏱️ **Speech Pacing**: Excellent pacing and natural pause intervals.")
        
    # Vocal Confidence Feedback
    if volume_penalty > 0.0:
        feedback.append("🔊 **Vocal Confidence**: The microphone signal is quite weak. Speak up or move closer to the microphone to demonstrate confidence and ensure clear transcription.")
    else:
        feedback.append("🔊 **Vocal Confidence**: Good volume level and clear projection.")
        
    feedback_notes = "\n\n".join(feedback)
    
    return {
        "semantic_score_base": base_score,
        "filler_penalty": filler_penalty,
        "pause_penalty": pause_penalty,
        "volume_penalty": volume_penalty,
        "overall_score": overall_score,
        "category": category,
        "feedback_notes": feedback_notes
    }
