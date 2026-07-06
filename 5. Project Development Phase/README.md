# Phase 5: Project Development Phase

This folder contains the active source code of the Voice-Based Concept Understanding Analyser (VBCUA) organized into decoupled frontend and backend subdirectories.

---

## 📁 Repository Code Structure

```text
5. Project Development Phase/
├── backend/                             # Core Processing Engine & Data Layer
│   ├── modules/                         # Core Python AI and Acoustic Modules
│   │   ├── audio_features.py            # Acoustic volume and silence analysis (Librosa)
│   │   ├── evaluation.py                # Scoring logic and penalty computations
│   │   ├── report_generator.py          # PDF flowable compiler (ReportLab)
│   │   ├── semantic_analysis.py         # Embedding similarity & filler word counting
│   │   └── transcription.py             # Speech transcoder (OpenAI Whisper)
│   ├── database.py                      # SQLAlchemy Relational database mappings
│   ├── requirements.txt                 # Backend dependencies
│   ├── inspect_db.py                    # Database utility script
│   └── test_sim.py                      # Offline scoring simulation script
│
└── frontend/                            # Presentation Dashboard Layer
    ├── app.py                           # Streamlit UI Dashboard Interface
    └── assets/                          # Static Assets
        ├── style.css                    # Custom CSS Cards and Dashboard theme
        └── dashboard_screenshot.png     # Application interface preview
```

---

## 💻 Running the Application

### 1. Run the Streamlit Dashboard
Launch the dashboard app from the project root workspace:
```bash
streamlit run "5. Project Development Phase/frontend/app.py"
```

---

## ⚙️ Project Development & Chronicles

### 1. Environment & Setup Chronicles
Development was initiated individually by setting up a Python virtual environment (`env`) under the project parent directory. Required libraries were installed via `pip` including PyTorch, Sentence-Transformers, Whisper, Librosa, Streamlit, and ReportLab. The code was structured modularly to isolate the UI, database connection, and individual intelligence modules.

### 2. Code Refactoring & Troubleshooting
During development, two major technical hurdles were resolved:
1. **The ffmpeg Dependency Issue**: Initial testing of Whisper threw a `FileNotFoundError` because Whisper's internal loader calls `ffmpeg` via a subprocess. We refactored `modules/transcription.py` to use `librosa.load(audio_path, sr=16000, mono=True)` which reads files natively, completely bypassing Whisper's ffmpeg dependency.
2. **ReportLab Unicode Rendering Crashes**: Emojis (like sparkles, thumbs-up, warning icons) used in feedback notes crashed ReportLab's standard Helvetica font. We implemented a custom `strip_emojis(text)` helper in `modules/report_generator.py` to clean all inputs before compiling the PDF.

### 3. Relational Schema Mapping
We constructed `database.py` utilizing SQLAlchemy's declarative base models. We wrote context-managed database sessions (`get_db()`) to prevent resource leaks and automatically seed default target concepts.
