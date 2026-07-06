# Voice-Based Concept Understanding Analyser (VBCUA)

VBCUA is a production-grade, local, and secure AI-powered assessment application designed to grade verbal concept explanations against reference concepts. It provides a modern, dark-themed presentation dashboard containing real-time metrics, diagnostic charts, text comparisons, and downloadable PDF report exports.

![VBCUA Evaluation Dashboard](assets/dashboard_screenshot.png)

---

## 🚀 Key Features

*   **Local Speech-to-Text**: High-accuracy transcription using OpenAI Whisper, resampled to 16,000 Hz and mixed down to mono to bypass external system `ffmpeg` dependencies.
*   **Semantic Concept Validation**: Piecewise non-linear similarity scoring using Sentence-BERT (`all-MiniLM-L6-v2`) to accurately grade paraphrased answers without penalizing natural word choice variations.
*   **Acoustic Pacing & Confidence Analysis**: Measures vocal volume projection (RMS energy) and silence gaps (pause ratio) using Librosa to evaluate speaking fluency.
*   **Persistent Database (SQLite)**: Fully relational schema mapping candidates, transcripts, evaluations, and reports utilizing SQLAlchemy 2.0.
*   **Exportable PDF Reports**: Professional flowable-based PDF generation using ReportLab with custom page borders and running headers/footers.

---

## 📁 Repository Structure

```text
VBCUA/
├── 1. Brainstorming & Ideation/           # Empathy Map & Conception Report (README.md)
├── 2. Requirement Analysis/               # SRS documentation (README.md)
├── 3. Project Design Phase/               # Architecture & Solution Fit reports (README.md)
├── 4. Project Planning Phase/             # Timeline and risk assessments (README.md)
├── 5. Project Development Phase/          # Restructured Codebase (README.md)
│   ├── backend/                           # Engine & Data Layer
│   │   ├── modules/                       # Transcription, Similarity & Audio feature modules
│   │   ├── database.py                    # SQLAlchemy models & seeds
│   │   ├── requirements.txt               # Backend Python dependencies
│   │   ├── inspect_db.py                  # Database inspection utility
│   │   └── test_sim.py                    # Offline pipeline scoring simulator
│   └── frontend/                          # Presentation Dashboard Layer
│       ├── app.py                         # Streamlit UI Presentation Dashboard
│       └── assets/                        # UI Stylesheet & Dashboard previews
├── 6.Project Testing/                     # Latency benchmarks and test plans (README.md)
├── 7.Project Documentation/               # Operator guides and user manuals (README.md)
├── 8.Project Demonstration/               # Showcase features, presentation guides (README.md)
├── .env.example                           # Configuration templates
├── .gitignore                             # Git exclusion boundaries
└── generate_academic_docs.py              # Compiles project phase PDF portfolios
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your operating system.

### 2. Clone and Setup Environment
Navigate to your project root folder and establish a virtual environment:
```bash
# Clone the repository
git clone <your-repository-url>
# Navigate to the workspace
cd VBCUA

# Create Python virtual environment
python -m venv env

# Activate the virtual environment (Windows)
.\env\Scripts\activate

# Activate the virtual environment (macOS/Linux)
source env/bin/activate
```

### 3. Install Dependencies
Install all required libraries for the backend/frontend engine:
```bash
pip install -r "5. Project Development Phase/backend/requirements.txt"
```

### 4. Setup Environment Variables
Copy `.env.example` to create your local `.env` configuration files:
```bash
# Root environment config
cp .env.example .env

# Subfolder environment configs (to support various execution contexts)
cp .env.example "5. Project Development Phase/frontend/.env"
cp .env.example "5. Project Development Phase/backend/.env"
```
Inside `.env`, verify or customize the defaults:
*   `DATABASE_URL`: Relational database connection string (SQLite fallback or remote PostgreSQL).
*   `WHISPER_MODEL_SIZE`: Whisper model configuration (e.g., `tiny`, `base`, `small`).
*   `SBERT_MODEL_NAME`: Sentence transformer model name (default: `all-MiniLM-L6-v2`).
*   `DEFAULT_SILENCE_THRESHOLD_DB`: Decibel threshold below peak to detect silence pauses.

---

## 💻 Running the Application

To launch the interactive Streamlit dashboard, run:
```bash
streamlit run "5. Project Development Phase/frontend/app.py"
```
This launches a local web server (typically at `http://localhost:8501`).

### 🎙️ How to Test and Run a Successful Demo:
1.  **Select Target Concept**: In the concept dropdown on the dashboard, select any pre-seeded target concept (e.g., **`Newton's First Law of Motion`** or **`Photosynthesis`**).
2.  **Upload Audio Response**: Upload a WAV or MP3 audio recording of yourself explaining the selected concept in your own words.
3.  **Run Analysis**: Click **Analyze Concept Understanding**. The system will transcribe the speech, match the semantic meaning, extract acoustic characteristics, and calculate your score.
4.  **Download PDF Report**: Click the download button to export a professionally styled, flowable-based PDF evaluation report.
5.  **View History**: Go to the **Assessment History** tab to view past evaluations or delete records from the SQLite/PostgreSQL database.

---

## 📝 Performance Benchmarks
Benchmark metrics recorded on sample inputs (tested on an Intel Core i7 processor):
*   **Whisper transcription (Warm Cache)**: ~1.26 seconds for a standard 2-second response.
*   **Semantic similarity (Warm Cache)**: ~0.028 seconds.
*   **Audio feature extraction**: ~0.004 seconds.
*   **PDF report compilation**: ~0.021 seconds.

---

## 🔒 Security & Privacy
All models (OpenAI Whisper, SentenceTransformer) run **100% locally** on your CPU/GPU. No audio recordings, transcripts, or grading scores are transmitted to external cloud servers, guaranteeing complete privacy of student response data.

