# Phase 2: Requirement Analysis

This folder contains the Software Requirements Specification (SRS) for the Voice-Based Concept Understanding Analyser (VBCUA). It defines the functional boundaries, system scope, and non-functional guarantees of the application.

---

## 📋 Software Requirements Specification (SRS)

### 1. System Scope & Objectives
The VBCUA is an assessment engine designed to capture student audio responses, transcribe them locally, check semantic similarity against a stored reference concept, analyze acoustic parameters, and compile a standardized evaluation. The primary goal is to provide a zero-latency, local, and secure evaluation environment.

### 2. Functional Requirements
* **FR-1 (Audio Ingestion)**: The system shall accept WAV and MP3 audio files via a file uploader, validating duration and file size.
* **FR-2 (Acoustic Feature Extraction)**: The system shall parse the raw audio file using Librosa to calculate duration, Root-Mean-Square (RMS) energy, and the proportion of silence intervals (pause ratio).
* **FR-3 (Local Transcription)**: The system shall transcribe the audio using OpenAI Whisper, bypassing external `ffmpeg` executable command-line installations on Windows by feeding pre-resampled mono numpy arrays directly into the Whisper decoder.
* **FR-4 (Semantic Evaluation)**: The system shall use the SentenceTransformer `all-MiniLM-L6-v2` model to calculate the cosine similarity between the transcription and the reference concept.
* **FR-5 (Fluency Analytics)**: The system shall scan the transcribed text using regex boundaries to count filler words (*"um"*, *"uh"*, *"like"*, *"ah"*, *"eh"*, *"so"*, *"actually"*, *"basically"*, *"you know"*) and compute a filler ratio.
* **FR-6 (Database Records)**: The system shall log all evaluations, users, sessions, audio features, similarity metrics, and report links to a local relational SQLite database using SQLAlchemy.
* **FR-7 (Report Compilation)**: The system shall generate a styled PDF report showing the score cards, text content comparison, and diagnostic recommendation notes.

### 3. Non-Functional Requirements
* **NFR-1 (Accuracy)**: The Whisper transcription must maintain a low Word Error Rate (WER) on clear English recordings. The Sentence-BERT semantic similarity must map to standard human grading metrics.
* **NFR-2 (Latency)**: Subsequent evaluations of cached models must execute in under 3 seconds.
* **NFR-3 (Data Security)**: All transcriptions and evaluations must be executed locally on the user's system; no audio files or texts shall be transmitted to external third-party APIs.
* **NFR-4 (Portability)**: The application shall run on any Windows system containing Python 3.10+ and the required packages.
