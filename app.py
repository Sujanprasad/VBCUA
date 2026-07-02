import streamlit as st
import os
import sys
import uuid
import json
import datetime
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()
from sqlalchemy.orm import joinedload

# Ensure modules directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database and modules
from database import (
    get_db, init_db, User, AudioFile, ReferenceConcept, 
    Transcript, FillerWordStats, SemanticSimilarity, 
    AudioFeature, EvaluationResult, Report, Session
)
from modules.transcription import transcribe_audio
from modules.semantic_analysis import compute_semantic_similarity, analyze_filler_words
from modules.audio_features import extract_audio_features
from modules.evaluation import evaluate_response
from modules.report_generator import generate_report_pdf

# Set page config
st.set_page_config(
    page_title="VBCUA - Voice-Based Concept Understanding Analyser",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Stylesheet
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback inline CSS if style.css is not found
        st.markdown("""
        <style>
        .metric-card {
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .metric-header { font-size: 14px; font-weight: 600; color: #94A3B8; margin-bottom: 5px; }
        .metric-value { font-size: 28px; font-weight: 700; color: #F8FAFC; }
        .metric-desc { font-size: 12px; color: #64748B; margin-top: 5px; }
        </style>
        """, unsafe_allow_html=True)

# 1. Initialize Database on startup
init_db()
load_css(os.path.join("assets", "style.css"))

# 2. Session Management
# Initialize a database-backed session token in st.session_state
if "session_token" not in st.session_state:
    st.session_state.session_token = uuid.uuid4().hex
    with get_db() as db:
        user = db.query(User).filter_by(username="default_user").first()
        if user:
            new_session = Session(
                user_id=user.id,
                session_token=st.session_state.session_token,
                login_time=datetime.datetime.utcnow(),
                last_activity=datetime.datetime.utcnow()
            )
            db.add(new_session)
            db.commit()
else:
    # Update last activity
    with get_db() as db:
        sess = db.query(Session).filter_by(session_token=st.session_state.session_token).first()
        if sess:
            sess.last_activity = datetime.datetime.utcnow()
            db.commit()

# Session State for retaining analysis results across operations (like download)
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# Custom metric card helper
def render_metric_card(header, value, desc):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">{header}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
st.sidebar.markdown("# 🛠️ Configuration")

# Load configuration from environment variables
default_model = os.getenv("WHISPER_MODEL_SIZE", "base").lower()
model_options = ["tiny", "base", "small"]
default_model_index = model_options.index(default_model) if default_model in model_options else 1

default_silence = abs(int(os.getenv("DEFAULT_SILENCE_THRESHOLD_DB", "25")))
if default_silence < 15 or default_silence > 40:
    default_silence = 25

# Model options
model_size = st.sidebar.selectbox(
    "Whisper Model Size",
    options=model_options,
    index=default_model_index,
    help="Tiny is faster, Base is more balanced, Small is slower but highly accurate."
)

# Librosa silence threshold
silence_threshold = st.sidebar.slider(
    "Silence Detection Threshold (dB)",
    min_value=15,
    max_value=40,
    value=default_silence,
    help="Higher values detect silence more easily; lower values require absolute quiet."
)

st.sidebar.divider()
st.sidebar.markdown("""
### 💡 How it works:
1. Select a reference concept in the main area (or add a new one in the **Concepts** tab).
2. Upload a audio response recording (WAV or MP3).
3. Click **Analyze Response**.
4. Review the AI-powered alignment grades, word pacing, and hesitation feedback.
5. Download your generated PDF report.
""")

st.sidebar.divider()
st.sidebar.info("Application powered by Whisper & Sentence-BERT")


# ----------------- MAIN LAYOUT -----------------
st.markdown("<h1 style='color: #0D9488;'>🎙️ Voice-Based Concept Understanding Analyser</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 16px; color: #94A3B8; margin-top: -15px;'>Evaluate and grade speech responses against reference concepts using AI.</p>", unsafe_allow_html=True)

tabs = st.tabs(["📊 Evaluation & Analysis", "📚 Reference Concepts", "📜 Assessment History"])

# ----------------- TAB 1: EVALUATION -----------------
with tabs[0]:
    # Load available reference concepts
    with get_db() as db:
        concepts = db.query(ReferenceConcept).all()
        
    if not concepts:
        st.warning("No reference concepts available. Please add some concepts first in the 'Reference Concepts' tab.")
        concepts_options = []
    else:
        concepts_options = concepts

    col_select, col_preview = st.columns([1, 2])
    
    with col_select:
        st.subheader("1. Select Target Concept")
        concept_titles = [c.title for c in concepts_options]
        selected_title = st.selectbox("Choose a Reference Concept", options=concept_titles)
        
        selected_concept = None
        for c in concepts_options:
            if c.title == selected_title:
                selected_concept = c
                break
                
    with col_preview:
        if selected_concept:
            st.subheader("Concept Preview")
            st.markdown(f"**Description:**\n*{selected_concept.concept_text}*")

    st.divider()
    
    st.subheader("2. Upload Audio Response")
    uploaded_file = st.file_uploader("Upload Audio response (.wav or .mp3)", type=["wav", "mp3"])
    
    if uploaded_file:
        st.audio(uploaded_file, format="audio/wav")
        
        # Action button
        analyze_btn = st.button("🚀 Analyze Concept Understanding", type="primary")
        
        if analyze_btn:
            # We will run the pipeline
            with st.spinner("Processing analysis pipeline... Please wait."):
                try:
                    # Save uploaded file temporarily
                    temp_dir = "temp_uploads"
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_filepath = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{uploaded_file.name}")
                    
                    with open(temp_filepath, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    file_size = os.path.getsize(temp_filepath)
                    
                    # 1. Transcription (Whisper)
                    status_text = st.empty()
                    status_text.text("✍️ Transcribing speech to text...")
                    trans_result = transcribe_audio(temp_filepath, model_name=model_size)
                    transcript_text = trans_result["text"]
                    word_count = trans_result["word_count"]
                    
                    if word_count == 0:
                        st.error("No speech detected in the audio file. Please try again with a clearer recording.")
                        status_text.empty()
                        if os.path.exists(temp_filepath):
                            os.remove(temp_filepath)
                    else:
                        # 2. Semantic Analysis
                        status_text.text("🧠 Calculating semantic understanding...")
                        similarity = compute_semantic_similarity(transcript_text, selected_concept.concept_text)
                        
                        # 3. Filler Word Extraction
                        status_text.text("🔍 Analysing filler words and pacing...")
                        filler_res = analyze_filler_words(transcript_text)
                        
                        # 4. Audio Feature Extraction (Librosa)
                        status_text.text("🔊 Extracting acoustic characteristics...")
                        audio_feats = extract_audio_features(temp_filepath, silence_threshold_db=silence_threshold)
                        
                        # 5. Grading and scoring
                        status_text.text("⚖️ Calculating final grades...")
                        eval_res = evaluate_response(
                            semantic_score=similarity,
                            filler_ratio=filler_res["filler_ratio"],
                            filler_word_count=filler_res["filler_word_count"],
                            pause_ratio=audio_feats["pause_ratio"],
                            rms_energy=audio_feats["rms_energy"],
                            word_count=word_count
                        )
                        
                        # 6. Database Write
                        status_text.text("💾 Saving records to SQLite...")
                        with get_db() as db:
                            user = db.query(User).filter_by(username="default_user").first()
                            
                            # Audio file entry
                            audio_file_db = AudioFile(
                                user_id=user.id,
                                filename=uploaded_file.name,
                                filepath=temp_filepath,
                                file_size=file_size,
                                duration_sec=audio_feats["duration_sec"]
                            )
                            db.add(audio_file_db)
                            db.commit()
                            db.refresh(audio_file_db)
                            
                            # Transcript entry
                            transcript_db = Transcript(
                                audio_file_id=audio_file_db.id,
                                transcript_text=transcript_text,
                                word_count=word_count
                            )
                            db.add(transcript_db)
                            db.commit()
                            db.refresh(transcript_db)
                            
                            # Filler words entry
                            filler_stats_db = FillerWordStats(
                                transcript_id=transcript_db.id,
                                filler_word_count=filler_res["filler_word_count"],
                                filler_ratio=filler_res["filler_ratio"],
                                filler_details=json.dumps(filler_res["filler_details"])
                            )
                            db.add(filler_stats_db)
                            
                            # Similarity entry
                            similarity_db = SemanticSimilarity(
                                transcript_id=transcript_db.id,
                                reference_concept_id=selected_concept.id,
                                similarity_score=similarity
                            )
                            db.add(similarity_db)
                            
                            # Audio feature entry
                            audio_feat_db = AudioFeature(
                                audio_file_id=audio_file_db.id,
                                pause_ratio=audio_feats["pause_ratio"],
                                rms_energy=audio_feats["rms_energy"],
                                duration_sec=audio_feats["duration_sec"]
                            )
                            db.add(audio_feat_db)
                            
                            # Evaluation results entry
                            eval_result_db = EvaluationResult(
                                audio_file_id=audio_file_db.id,
                                reference_concept_id=selected_concept.id,
                                semantic_similarity_score=similarity,
                                filler_word_penalty=eval_res["filler_penalty"],
                                audio_features_score=eval_res["pause_penalty"],
                                overall_score=eval_res["overall_score"],
                                category=eval_res["category"],
                                feedback_notes=eval_res["feedback_notes"],
                                created_at=datetime.datetime.utcnow()
                            )
                            db.add(eval_result_db)
                            db.commit()
                            db.refresh(eval_result_db)
                            
                            # 7. Generate PDF Report
                            status_text.text("📄 Generating PDF summary...")
                            reports_dir = "reports"
                            os.makedirs(reports_dir, exist_ok=True)
                            pdf_filepath = os.path.join(reports_dir, f"report_eval_{eval_result_db.id}.pdf")
                            
                            report_data = {
                                "username": user.username,
                                "concept_title": selected_concept.title,
                                "concept_text": selected_concept.concept_text,
                                "transcript_text": transcript_text,
                                "word_count": word_count,
                                "semantic_score_base": similarity * 100.0,
                                "filler_word_count": filler_res["filler_word_count"],
                                "filler_ratio": filler_res["filler_ratio"],
                                "filler_penalty": eval_res["filler_penalty"],
                                "pause_ratio": audio_feats["pause_ratio"],
                                "pause_penalty": eval_res["pause_penalty"],
                                "rms_energy": audio_feats["rms_energy"],
                                "volume_penalty": eval_res["volume_penalty"],
                                "overall_score": eval_res["overall_score"],
                                "category": eval_res["category"],
                                "feedback_notes": eval_res["feedback_notes"],
                                "created_at": eval_result_db.created_at
                            }
                            
                            generate_report_pdf(report_data, pdf_filepath)
                            
                            # Report entry
                            report_db = Report(
                                evaluation_result_id=eval_result_db.id,
                                pdf_filepath=pdf_filepath
                            )
                            db.add(report_db)
                            db.commit()
                            
                            # Cache in session state
                            st.session_state.analysis_results = report_data
                            st.session_state.analysis_results["pdf_filepath"] = pdf_filepath
                            
                        status_text.empty()
                        st.success("✅ Analysis completed successfully!")
                
                except Exception as e:
                    st.error(f"An error occurred during evaluation: {e}")
                    import traceback
                    st.code(traceback.format_exc())
                    
    # Render results if present in session state
    if st.session_state.analysis_results:
        res = st.session_state.analysis_results
        st.divider()
        st.subheader("📊 Analysis Results Summary")
        
        # Columns for metrics
        c1, c2, c3, c4 = st.columns(4)
        
        # Display overall score and category
        cat_badge = ""
        if res["category"] == "Strong":
            cat_badge = f"<span class='badge badge-strong'>{res['category']}</span>"
        elif res["category"] == "Moderate":
            cat_badge = f"<span class='badge badge-moderate'>{res['category']}</span>"
        else:
            cat_badge = f"<span class='badge badge-poor'>{res['category']}</span>"
            
        with c1:
            render_metric_card(
                "Overall Score", 
                f"{res['overall_score']:.1f} / 100", 
                f"Assessment Rating: {cat_badge}"
            )
        with c2:
            render_metric_card(
                "Semantic Similarity", 
                f"{res['semantic_score_base']:.1f}%", 
                "Concept overlap metric"
            )
        with c3:
            render_metric_card(
                "Speech Pacing", 
                f"{res['pause_ratio']:.1%} pauses", 
                f"Pause Penalty: -{res['pause_penalty']:.1f} pts"
            )
        with c4:
            render_metric_card(
                "Fluency Ratio", 
                f"{res['filler_ratio']:.1%}", 
                f"Filler count: {res['filler_word_count']} (-{res['filler_penalty']:.1f} pts)"
            )
            
        # Download PDF button
        if os.path.exists(res.get("pdf_filepath", "")):
            with open(res["pdf_filepath"], "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Detailed PDF Report",
                    data=pdf_file,
                    file_name=f"VBCUA_Report_{res['concept_title'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
        
        # Comparison layout
        st.markdown("### 📝 Text Content Comparison")
        col_trans, col_ref = st.columns(2)
        
        with col_trans:
            st.markdown(f"""
            <div class="content-box-header">Transcribed Student Answer ({res['word_count']} words)</div>
            <div class="content-box">{res['transcript_text']}</div>
            """, unsafe_allow_html=True)
            
        with col_ref:
            st.markdown(f"""
            <div class="content-box-header">Reference Concept definition</div>
            <div class="content-box">{res['concept_text']}</div>
            """, unsafe_allow_html=True)
            
        # Diagnostics
        st.markdown("### 📋 Diagnostic Insights & Recommendations")
        st.markdown(f"""
        <div class="custom-feedback-card">
            <div class="feedback-section-title">SCORING AUDIT NOTES</div>
            {res['feedback_notes'].replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)


# ----------------- TAB 2: REFERENCE CONCEPTS -----------------
with tabs[1]:
    st.subheader("📚 Reference Concepts Database")
    
    # Reload concepts
    with get_db() as db:
        concepts = db.query(ReferenceConcept).all()
        
    if concepts:
        concept_list = []
        for c in concepts:
            concept_list.append({
                "ID": c.id,
                "Title": c.title,
                "Concept Text Length": len(c.concept_text),
                "Created At": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        st.table(concept_list)
    else:
        st.info("No reference concepts available.")
        
    st.divider()
    
    st.subheader("➕ Add New Reference Concept")
    with st.form("add_concept_form", clear_on_submit=True):
        new_title = st.text_input("Concept Title", placeholder="e.g., Photosynthesis")
        new_text = st.text_area("Concept Text Definition", placeholder="Write the reference explanation that users should cover...")
        submit_btn = st.form_submit_button("Add Concept", type="primary")
        
        if submit_btn:
            if new_title.strip() and new_text.strip():
                with get_db() as db:
                    # Check if exists
                    existing = db.query(ReferenceConcept).filter_by(title=new_title.strip()).first()
                    if existing:
                        st.error(f"Concept titled '{new_title.strip()}' already exists.")
                    else:
                        new_concept = ReferenceConcept(
                            title=new_title.strip(),
                            concept_text=new_text.strip(),
                            created_at=datetime.datetime.utcnow()
                        )
                        db.add(new_concept)
                        db.commit()
                        st.success(f"Successfully added concept: {new_title}")
                        st.rerun()
            else:
                st.warning("Please fill in both the Title and the Concept Text.")


# ----------------- TAB 3: ASSESSMENT HISTORY -----------------
with tabs[2]:
    st.subheader("📜 Historical Evaluations")
    
    with get_db() as db:
        # Load evaluations with joined audio and reference concepts
        evals = db.query(EvaluationResult).options(
            joinedload(EvaluationResult.audio_file),
            joinedload(EvaluationResult.reference_concept)
        ).order_by(EvaluationResult.created_at.desc()).all()
        
    if not evals:
        st.info("No evaluations have been performed yet.")
    else:
        history_list = []
        eval_map = {}
        
        for e in evals:
            # Format title
            concept_title = e.reference_concept.title if e.reference_concept else "N/A"
            filename = e.audio_file.filename if e.audio_file else "N/A"
            date_str = e.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            history_list.append({
                "Evaluation ID": e.id,
                "Concept": concept_title,
                "Audio File": filename,
                "Overall Score": f"{e.overall_score:.1f}",
                "Category": e.category,
                "Performed On": date_str
            })
            eval_map[e.id] = e
            
        st.dataframe(history_list, use_container_width=True)
        
        st.divider()
        st.subheader("🔍 Review Past Evaluation Details")
        
        eval_ids = [e["Evaluation ID"] for e in history_list]
        selected_eval_id = st.selectbox("Select Evaluation Run ID to View Details", options=eval_ids)
        
        if selected_eval_id:
            e = eval_map[selected_eval_id]
            
            # Load joined tables
            with get_db() as db:
                # Load transcription details and filler details
                transcript = db.query(Transcript).options(
                    joinedload(Transcript.filler_word_stats)
                ).filter_by(audio_file_id=e.audio_file_id).first()
                
                audio_feat = db.query(AudioFeature).filter_by(audio_file_id=e.audio_file_id).first()
                report_rec = db.query(Report).filter_by(evaluation_result_id=e.id).first()
            
            # Reconstruct details
            h_score = e.overall_score
            h_cat = e.category
            h_text = transcript.transcript_text if transcript else "N/A"
            h_word_count = transcript.word_count if transcript else 0
            h_ref_text = e.reference_concept.concept_text if e.reference_concept else "N/A"
            h_ref_title = e.reference_concept.title if e.reference_concept else "N/A"
            
            h_filler_count = transcript.filler_word_stats.filler_word_count if (transcript and transcript.filler_word_stats) else 0
            h_filler_ratio = transcript.filler_word_stats.filler_ratio if (transcript and transcript.filler_word_stats) else 0.0
            
            h_pause_ratio = audio_feat.pause_ratio if audio_feat else 0.0
            h_rms = audio_feat.rms_energy if audio_feat else 0.0
            
            # Display
            hc1, hc2, hc3, hc4 = st.columns(4)
            
            h_badge = ""
            if h_cat == "Strong":
                h_badge = f"<span class='badge badge-strong'>{h_cat}</span>"
            elif h_cat == "Moderate":
                h_badge = f"<span class='badge badge-moderate'>{h_cat}</span>"
            else:
                h_badge = f"<span class='badge badge-poor'>{h_cat}</span>"
                
            with hc1:
                render_metric_card("Overall Score", f"{h_score:.1f} / 100", f"Assessment: {h_badge}")
            with hc2:
                render_metric_card("Semantic Similarity", f"{e.semantic_similarity_score*100:.1f}%", "Concept overlap metric")
            with hc3:
                render_metric_card("Speech Pacing", f"{h_pause_ratio:.1%} pauses", f"Pause Penalty: -{e.audio_features_score:.1f} pts")
            with hc4:
                render_metric_card("Fluency Ratio", f"{h_filler_ratio:.1%}", f"Filler Count: {h_filler_count} (-{e.filler_word_penalty:.1f} pts)")
                
            # Download PDF Report button
            if report_rec and os.path.exists(report_rec.pdf_filepath):
                with open(report_rec.pdf_filepath, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Download Historical PDF Report",
                        data=pdf_file,
                        file_name=f"VBCUA_Historical_Report_{h_ref_title.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_hist_{e.id}"
                    )
            else:
                st.warning("PDF report file is missing or was not generated for this run.")
                
            # Comparison
            st.markdown("### 📝 Text Content Comparison")
            col_h_trans, col_h_ref = st.columns(2)
            
            with col_h_trans:
                st.markdown(f"""
                <div class="content-box-header">Transcribed Student Answer ({h_word_count} words)</div>
                <div class="content-box">{h_text}</div>
                """, unsafe_allow_html=True)
                
            with col_h_ref:
                st.markdown(f"""
                <div class="content-box-header">Reference Concept definition</div>
                <div class="content-box">{h_ref_text}</div>
                """, unsafe_allow_html=True)
                
            # Feedback
            st.markdown("### 📋 Diagnostic Insights & Recommendations")
            st.markdown(f"""
            <div class="custom-feedback-card">
                <div class="feedback-section-title">SCORING AUDIT NOTES</div>
                {e.feedback_notes.replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            # Action to delete
            st.markdown("---")
            if st.button("🗑️ Delete this Evaluation Run", key=f"del_eval_{e.id}", type="secondary"):
                with get_db() as db:
                    # Load and delete
                    eval_to_delete = db.query(EvaluationResult).filter_by(id=e.id).first()
                    if eval_to_delete:
                        # Also delete corresponding audio file from disk
                        audio_rec = db.query(AudioFile).filter_by(id=eval_to_delete.audio_file_id).first()
                        if audio_rec and os.path.exists(audio_rec.filepath):
                            try:
                                os.remove(audio_rec.filepath)
                            except Exception as ex:
                                print(f"Error removing audio file: {ex}")
                                
                        # Delete report from disk
                        rep_rec = db.query(Report).filter_by(evaluation_result_id=eval_to_delete.id).first()
                        if rep_rec and os.path.exists(rep_rec.pdf_filepath):
                            try:
                                os.remove(rep_rec.pdf_filepath)
                            except Exception as ex:
                                print(f"Error removing report PDF: {ex}")
                                
                        db.delete(eval_to_delete)
                        db.commit()
                        st.success("Successfully deleted evaluation run.")
                        st.rerun()