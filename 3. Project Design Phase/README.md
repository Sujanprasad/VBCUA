# Phase 3: Project Design Phase

This folder contains the engineering design for the Voice-Based Concept Understanding Analyser (VBCUA). It covers the Problem-Solution Fit validation, technical stack details, component blueprints, and the database relational schema.

---

## ⚖️ Problem-Solution Fit Validation

### 1. Problem Statement
Traditional written tests fail to capture a student's active recall and verbal communication capabilities. Verbal testing (vivas/presentations) is ideal, but manually grading hours of audio explanations is highly subjective, labor-intensive, and unfeasible for large classes. EdTech tools currently lack local, private, and automatic systems for speech-concept analysis.

### 2. Proposed Solution Fit
The Voice-Based Concept Understanding Analyser (VBCUA) solves this bottleneck by establishing automated pipelines:
* **Speech to Text**: Bypasses manual transcription by converting spoken audio to text locally using Whisper.
* **Semantic Scoring**: Matches the candidate's explanation against a verified reference concept using Sentence-BERT embeddings, checking for conceptual understanding rather than mere keyword match.
* **Fluency Assessment**: Detects filler words and silent hesitations, scoring vocal projection (average RMS energy) to grade speaking confidence.

### 3. Verification of Fit
The fit is verified when the automatic grading system provides scores that map to standard human evaluations (Strong, Moderate, Poor), flags specific filler word habits, and outputs downloadable PDFs that students can use to guide self-study.

---

## 🛠️ Proposed System Solution & Technical Spec

### 1. Technical Stack Selection
* **Streamlit**: Selected for the UI because it allows building clean, interactive dashboard components and managing session state natively in Python.
* **SQLAlchemy & SQLite/Supabase PostgreSQL**: Provides local or remote relational database storage, mapping candidate transcripts, audio features, and reports cleanly.
* **OpenAI Whisper (Local)**: Selected for transcription as it runs locally and is robust to background noise and minor stuttering.
* **SentenceTransformer (`all-MiniLM-L6-v2`)**: Used to calculate semantic embeddings; it is extremely lightweight, fast, and maintains high semantic correlation.
* **Librosa & Soundfile**: Used to load audio, calculate RMS energy, and isolate silent intervals (using energy thresholds).

### 2. Core Processing Sequence
1. User uploads WAV/MP3 file and selects reference concept.
2. Audio file is loaded via Librosa, resampled to 16,000 Hz, and converted to a mono array.
3. Whisper transcribes the mono array; total word count is calculated.
4. S-BERT computes cosine similarity between the transcript and the concept text.
5. Text is scanned for filler words to calculate the filler ratio.
6. Librosa isolates non-speech silence frames using decibel thresholds to compute the pause ratio.
7. The scoring engine deducts penalties for fillers, excessive silence, and low volume, calculating the final grade.
8. Evaluation data is logged in the database, and ReportLab compiles a PDF report.

---

## 🏗️ Solution Architecture & Relational Schema

### 1. System Components
The VBCUA is structured into three main layers:
1. **Presentation Layer**: Managed by `app.py`, which renders the Streamlit pages, collects configuration parameters (silence thresholds, model sizes), displays interactive analysis cards, and handles file download streams.
2. **Business Logic Layer**: Located under `modules/` which isolates transcription, semantic evaluation, audio feature extraction, and report creation.
3. **Database Layer**: Handled by `database.py` which defines SQLAlchemy tables and manages sessions.

### 2. Relational Schema Tables
* **USER**: Stores user details (username, email).
* **SESSION**: Tracks active sessions linked to users.
* **AUDIO_FILE**: Stores filename, file size, filepath, and duration.
* **REFERENCE_CONCEPT**: Stores reference concepts (Photosynthesis, Neural Networks, etc.).
* **TRANSCRIPT**: Stores transcribed text and word count.
* **FILLER_WORD_STATS**: Stores total filler word counts, ratios, and JSON details.
* **SEMANTIC_SIMILARITY**: Stores the raw Sentence-BERT similarity score.
* **AUDIO_FEATURE**: Stores extracted Librosa metrics (pause ratio, rms energy).
* **EVALUATION_RESULT**: Integrates overall score, category, and feedback notes.
* **REPORT**: Tracks pdf filepaths and creation timestamps.
