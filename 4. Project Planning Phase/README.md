# Phase 4: Project Planning Phase

This folder contains the planning documents, schedules, milestones, and risk mitigation strategies for the Voice-Based Concept Understanding Analyser (VBCUA).

---

## 📅 Project Planning & Milestone Schedule

### 1. Milestones & Phases
* **Phase 1 (Database & Setup)**: Set up SQLite schema and populate mock concepts. *Duration: 3 days.*
* **Phase 2 (AI Engine & Audio Logic)**: Develop Whisper transcription, Librosa audio feature extraction, and Sentence-BERT similarity modules. *Duration: 5 days.*
* **Phase 3 (Dashboard & Presentation)**: Construct Streamlit UI, load custom CSS stylesheets, and design ReportLab PDF templates. *Duration: 4 days.*
* **Phase 4 (Validation & Optimization)**: Run performance benchmarks, implement model caching, and test edge cases. *Duration: 3 days.*

### 2. Risk Analysis & Mitigation
* **Risk 1: Missing ffmpeg Dependency on Target Windows Machine**
  * *Impact*: High. Breaks Whisper's default file loader.
  * *Mitigation*: Bypassed ffmpeg by using Librosa to read audio files directly and passing pre-processed numpy arrays to Whisper's transcribe function.
* **Risk 2: Model Loading Latency**
  * *Impact*: Medium. Reloading heavy models on every click breaks UI responsiveness.
  * *Mitigation*: Wrapped model loading in Streamlit's `@st.cache_resource` caching wrapper.
