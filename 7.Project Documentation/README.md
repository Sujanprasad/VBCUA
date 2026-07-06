# Phase 7: Project Documentation

This folder contains the operator guides, system configuration parameters, and user manual for the Voice-Based Concept Understanding Analyser (VBCUA).

---

## 📖 User Manual & System Operator Guide

### 1. Local Execution Guide
To launch the application locally:
1. Open a terminal in the project root directory.
2. Activate your Python virtual environment:
   ```bash
   # Windows
   .\env\Scripts\activate
   
   # macOS/Linux
   source env/bin/activate
   ```
3. Install required libraries if not already done:
   ```bash
   pip install -r "5. Project Development Phase/backend/requirements.txt"
   ```
4. Execute the Streamlit command:
   ```bash
   streamlit run "5. Project Development Phase/frontend/app.py"
   ```
5. Access the local port in your browser: `http://localhost:8501`.

### 2. Functional Interface Walkthrough
* **Evaluation & Analysis Tab**: Select your target concept from the pre-populated dropdown, upload a WAV/MP3 audio recording, review the analysis dashboard, and download the PDF report.
* **Reference Concepts Tab**: Manage the SQLite reference database. Add a new concept by typing its title and reference explanation text.
* **Assessment History Tab**: Access previous evaluations, view detailed metrics and side-by-side text comparisons, download past PDF reports, or delete past runs (CRUD).

### 3. Administrator Configurations
In the sidebar, administrators can adjust the Whisper model size (`tiny`, `base`, `small`) and set the Librosa silence threshold (dB) depending on background noise levels.
