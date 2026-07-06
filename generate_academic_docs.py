import os
import sys
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def draw_page_decorations(canvas, doc):
    """
    Draws a professional teal border, running header, and footer on every page.
    """
    canvas.saveState()
    
    # 1. Border
    canvas.setStrokeColor(colors.HexColor("#0D9488"))  # Teal 600
    canvas.setLineWidth(1.5)
    # Letter size is 612 x 792. Draw rect with 36pt margins.
    canvas.rect(36, 36, 540, 720)
    
    # 2. Running Header Line
    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))  # Slate 200
    canvas.setLineWidth(0.75)
    canvas.line(54, 735, 558, 735)
    
    # 3. Running Header Text
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor("#475569"))  # Slate 600
    canvas.drawString(54, 742, "VBCUA - SYSTEM ASSESSMENT & PORTFOLIO DOCUMENTATION")
    
    # 4. Running Footer Line
    canvas.line(54, 55, 558, 55)
    
    # 5. Running Footer Text
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))  # Slate 500
    canvas.drawString(54, 42, "INDIVIDUAL CAPSTONE PROJECT - SOLE DEVELOPER SUJAN PRASAD")
    
    # 6. Page Number
    page_num = canvas.getPageNumber()
    canvas.drawRightString(558, 42, f"Page {page_num}")
    
    canvas.restoreState()

def create_professional_pdf(filepath, doc_title, subtitle, content_blocks, table_blocks=None):
    """
    Compiles a highly styled, professional PDF report inside the system borders.
    """
    filepath = os.path.abspath(filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Left/Right margin 54pt (0.75in), Top/Bottom margins set to clear headers/footers
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=80,
        bottomMargin=70
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F766E"),  # Teal 700
        spaceAfter=4,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#64748B"),  # Slate 500
        spaceAfter=15,
        alignment=1
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1E293B"),  # Slate 800
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),  # Slate 700
        spaceAfter=8
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )
    
    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )
    
    story = []
    story.append(Spacer(1, 10))
    story.append(Paragraph(doc_title.upper(), title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(Spacer(1, 10))
    
    # 1. Render Tables if provided
    if table_blocks:
        for tab_title, data, col_widths, is_grid in table_blocks:
            if tab_title:
                story.append(Paragraph(tab_title, h2_style))
                story.append(Spacer(1, 4))
            
            formatted_data = []
            for row_idx, row in enumerate(data):
                formatted_row = []
                for cell in row:
                    if row_idx == 0 and is_grid:
                        formatted_row.append(Paragraph(cell, table_header_style))
                    else:
                        formatted_row.append(Paragraph(cell, table_body_style))
                formatted_data.append(formatted_row)
                
            t = Table(formatted_data, colWidths=col_widths)
            
            t_style = [
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]
            if is_grid:
                t_style += [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F766E")),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ]
            else:
                t_style += [
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
                    ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8FAFC")),
                ]
            t.setStyle(TableStyle(t_style))
            story.append(t)
            story.append(Spacer(1, 12))
            
    # 2. Render Text Content Blocks
    for block_title, paragraphs in content_blocks:
        story.append(Paragraph(block_title, h2_style))
        story.append(Spacer(1, 4))
        for p in paragraphs:
            story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 10))
        
    doc.build(story, onFirstPage=draw_page_decorations, onLaterPages=draw_page_decorations)

def main():
    print("Generating expanded, professional portfolio documentation...")

    # ==================== 1. PROJECT CONCEPTION ====================
    # 1.1 Empathy Map
    create_professional_pdf(
        "1. Brainstorming & Ideation/Empathy Map.pdf",
        "Empathy Map - VBCUA User Analysis",
        "Deep Analysis of Student and Instructor Persona Behaviors & Needs",
        [
            ("1. Executive Summary", [
                "Understanding how candidates formulate and deliver conceptual explanations is vital for automated education grading systems. The Voice-Based Concept Understanding Analyser (VBCUA) target persona maps to two major user segments: Students (who need objective, instant conceptual validation) and Instructors (who need to assess students' active vocabulary without subjective grading bottlenecks)."
            ]),
            ("2. What Users THINK & FEEL", [
                "• **Students**: They often think, 'How accurate is this semantic matching engine?', 'Will my regional accent or a brief stutter lower my score?', and 'I need immediate grading on my explanation so I can fix my conceptual gaps before the final exam.'",
                "• **Instructors**: They feel overwhelmed by manual grading cycles, thinking, 'I spend too many hours listening to audio recordings manually.', 'I want to know if my students are merely memorizing definitions verbatim or if they understand the actual logical dependencies of the subject matter.'"
            ]),
            ("3. What Users SAY & DO", [
                "• **Students**: They say, 'I know the topic, but I find it hard to explain it verbally in class.' During verbal assessments, they tend to pause frequently, use filler words (like 'um', 'uh', 'like') when searching for terminology, and actively request structured diagnostics to improve.",
                "• **Instructors**: They say, 'I want to assign more oral exams, but I don't have the time to grade them objectively for 100 students.' They record student explanations, check them against a checklist, and write feedback manually."
            ]),
            ("4. Customer Pains & Gains", [
                "• **Pains (Bottlenecks)**: Subjective grading of spoken answers, delayed feedback cycles, lack of clear metrics showing speech fluency or vocal confidence, and high anxiety during verbal exams.",
                "• **Gains (Value Delivered)**: Instant objective grading, transparent feedback on filler word counts and pause ratios, side-by-side text comparisons, and structured, actionable diagnostic notes showing clear areas of conceptual improvement."
            ])
        ]
    )

    # 1.2 Project Conception Report
    create_professional_pdf(
        "1. Brainstorming & Ideation/Project Conception Report.pdf",
        "Project Conception & Design Thinking Report",
        "Detailed Conception, Persona Identification, and Problem Definition",
        [
            ("1. Project Background & Initiation", [
                "In modern education, assessing conceptual understanding via verbal communication is key. However, manual grading of spoken explanations is time-consuming and subjective. The Voice-Based Concept Understanding Analyser (VBCUA) was conceived to automate this process locally, privately, and securely."
            ]),
            ("2. User Personas & Empathy Map Details", [
                "• **Student Persona**: Needs immediate feedback on oral explanations, worries about grading bias, and wants actionable metrics to improve speech fluency.",
                "• **Instructor Persona**: Manages large classes, spends excessive hours listening to audio recordings, and seeks an objective helper to check semantic concept matching and speech pacing."
            ]),
            ("3. Brainstorming & Ideation Phase", [
                "During the ideation phase, various architectural approaches were evaluated. The team decided on a local-first AI system combining OpenAI Whisper for transcription, Sentence-BERT for semantic similarity matching, and Librosa for extracting acoustic characteristics (volume and silence pauses). This avoids external API costs and secures user privacy."
            ]),
            ("4. Problem-Solution Fit", [
                "The fit is achieved by mapping the candidate's spoken text directly to stored reference concepts in a local relational database, calculating a combined content-delivery score, and generating a professional, downloadable feedback report in PDF format."
            ])
        ]
    )


    # ==================== 2. REQUIREMENT ANALYSIS ====================
    create_professional_pdf(
        "2. Requirement Analysis/Software Requirements Specification.pdf",
        "Software Requirements Specification (SRS)",
        "System Scope, Functional, and Non-Functional Requirements for VBCUA",
        [
            ("1. System Scope & Objectives", [
                "The VBCUA is a desktop/web-based assessment engine designed to capture student audio responses, transcribe them locally, check semantic similarity against a stored reference concept, analyze acoustic parameters, and compile a standardized evaluation. The primary goal is to provide a zero-latency, local, and secure evaluation environment."
            ]),
            ("2. Functional Requirements", [
                "• **FR-1 (Audio Ingestion)**: The system shall accept WAV and MP3 audio files via a file uploader, validating duration and file size.",
                "• **FR-2 (Acoustic Feature Extraction)**: The system shall parse the raw audio file using Librosa to calculate duration, Root-Mean-Square (RMS) energy, and the proportion of silence intervals (pause ratio).",
                "• **FR-3 (Local Transcription)**: The system shall transcribes the audio using OpenAI Whisper, bypassing external ffmpeg executable command-line installations on Windows by feeding pre-resampled mono numpy arrays directly into the Whisper decoder.",
                "• **FR-4 (Semantic Evaluation)**: The system shall use the SentenceTransformer 'all-MiniLM-L6-v2' model to calculate the cosine similarity between the transcription and the reference concept.",
                "• **FR-5 (Fluency Analytics)**: The system shall scan the transcribed text using regex boundaries to count filler words ('um', 'uh', 'like', 'ah', 'eh', 'so', 'actually', 'basically', 'you know') and compute a filler ratio.",
                "• **FR-6 (Database Records)**: The system shall log all evaluations, users, sessions, audio features, similarity metrics, and report links to a local relational SQLite database using SQLAlchemy.",
                "• **FR-7 (Report Compilation)**: The system shall generate a styled PDF report showing the score cards, text content comparison, and diagnostic recommendation notes."
            ]),
            ("3. Non-Functional Requirements", [
                "• **NFR-1 (Accuracy)**: The Whisper transcription must maintain a low Word Error Rate (WER) on clear english recordings. The Sentence-BERT semantic similarity must map to standard human grading metrics.",
                "• **NFR-2 (Latency)**: Subsequent evaluations of cached models must execute in under 3 seconds.",
                "• **NFR-3 (Data Security)**: All transcriptions and evaluations must be executed locally on the user's system; no audio files or texts shall be transmitted to external third-party APIs.",
                "• **NFR-4 (Portability)**: The application shall run on any Windows system containing Python 3.10+ and the required packages."
            ])
        ]
    )

    # ==================== 3. PROJECT DESIGN PHASE ====================
    # 3.1 Problem-Solution Fit
    create_professional_pdf(
        "3. Project Design Phase/Problem-Solution Fit.pdf",
        "Problem-Solution Fit Validation",
        "Validating Educational Pains and Technical Capabilities Alignment",
        [
            ("1. Problem Statement", [
                "Traditional written tests fail to capture a student's active recall and verbal communication capabilities. Verbal testing (vivas/presentations) is ideal, but manually grading hours of audio explanations is highly subjective, labor-intensive, and unfeasible for large classes. EdTech tools currently lack local, private, and automatic systems for speech-concept analysis."
            ]),
            ("2. Proposed Solution Fit", [
                "The Voice-Based Concept Understanding Analyser (VBCUA) solves this bottleneck by establishing an automated pipelines:",
                "• **Speech to Text**: Bypasses manual transcription by converting spoken audio to text locally using Whisper.",
                "• **Semantic Scoring**: Matches the candidate's explanation against a verified reference concept using Sentence-BERT embeddings, checking for conceptual understanding rather than mere keyword match.",
                "• **Fluency Assessment**: Detects filler words and silent hesitations, scoring vocal projection (average RMS energy) to grade speaking confidence."
            ]),
            ("3. Verification of Fit", [
                "The fit is verified when the automatic grading system provides scores that map to standard human evaluations (Strong, Moderate, Poor), flags specific filler word habits, and outputs downloadable PDFs that students can use to guide self-study."
            ])
        ]
    )

    # 3.2 Proposed Solution
    create_professional_pdf(
        "3. Project Design Phase/Proposed Solution.pdf",
        "Proposed System Solution & Technical Spec",
        "Design Details of the Presentation and Core Intelligence Layer",
        [
            ("1. Technical Stack Selection", [
                "• **Streamlit**: Selected for the UI because it allows building clean, interactive dashboard components and managing session state natively in Python.",
                "• **SQLAlchemy & SQLite**: Provides a local relational database storage schema, mapping candidate transcripts, audio features, and reports cleanly.",
                "• **OpenAI Whisper (Local)**: Selected for transcription as it runs locally and is robust to background noise and minor stuttering.",
                "• **SentenceTransformer ('all-MiniLM-L6-v2')**: Used to calculate semantic embeddings; it is extremely lightweight, fast, and maintains high semantic correlation.",
                "• **Librosa & Soundfile**: Used to load audio, calculate RMS energy, and isolate silent intervals (using energy thresholds)."
            ]),
            ("2. Core Processing Sequence", [
                "1. User uploads WAV/MP3 file and selects reference concept.",
                "2. Audio file is loaded via Librosa, resampled to 16,000 Hz, and converted to a mono array.",
                "3. Whisper transcribes the mono array; total word count is calculated.",
                "4. S-BERT computes cosine similarity between the transcript and the concept text.",
                "5. Text is scanned for filler words to calculate the filler ratio.",
                "6. Librosa isolates non-speech silence frames using decibel thresholds to compute the pause ratio.",
                "7. The scoring engine deducts penalties for fillers, excessive silence, and low volume, calculating the final grade.",
                "8. Evaluation data is logged in the database, and ReportLab compiles a PDF report."
            ])
        ]
    )

    # 3.3 Solution Architecture
    create_professional_pdf(
        "3. Project Design Phase/Solution Architecture.pdf",
        "Solution Architecture & Relational Schema",
        "Detailed Database Entity Schema and System Component Layout",
        [
            ("1. System Components", [
                "The VBCUA is structured into three main layers:",
                "1. **Presentation Layer**: Managed by `app.py`, which renders the Streamlit pages, collects configuration parameters (silence thresholds, model sizes), displays interactive analysis cards, and handles file download streams.",
                "2. **Business Logic Layer**: Located under `modules/` which isolates transcription, semantic evaluation, audio feature extraction, and report creation.",
                "3. **Database Layer**: Handled by `database.py` which defines SQLAlchemy tables and manages sessions."
            ]),
            ("2. Relational Schema Tables", [
                "• **USER**: Stores user details (username, email).",
                "• **SESSION**: Tracks active sessions linked to users.",
                "• **AUDIO_FILE**: Stores filename, file size, filepath, and duration.",
                "• **REFERENCE_CONCEPT**: Stores reference concepts (Photosynthesis, Neural Networks, etc.).",
                "• **TRANSCRIPT**: Stores transcribed text and word count.",
                "• **FILLER_WORD_STATS**: Stores total filler word counts, ratios, and JSON details.",
                "• **SEMANTIC_SIMILARITY**: Stores the raw Sentence-BERT similarity score.",
                "• **AUDIO_FEATURE**: Stores extracted Librosa metrics (pause ratio, rms energy).",
                "• **EVALUATION_RESULT**: Integrates overall score, category, and feedback notes.",
                "• **REPORT**: Tracks pdf filepaths and creation timestamps."
            ])
        ]
    )

    # ==================== 4. PROJECT PLANNING PHASE ====================
    create_professional_pdf(
        "4. Project Planning Phase/Project Planning.pdf",
        "Project Planning & Milestone Schedule",
        "Development Timeline, Risk Assessment, and Resource Allocation Plan",
        [
            ("1. Milestones & Phases", [
                "• **Phase 1 (Database & Setup)**: Set up SQLite schema and populate mock concepts. Duration: 3 days.",
                "• **Phase 2 (AI Engine & Audio Logic)**: Develop Whisper transcription, Librosa audio feature extraction, and Sentence-BERT similarity modules. Duration: 5 days.",
                "• **Phase 3 (Dashboard & Presentation)**: Construct Streamlit UI, load custom CSS stylesheets, and design ReportLab PDF templates. Duration: 4 days.",
                "• **Phase 4 (Validation & Optimization)**: Run performance benchmarks, implement model caching, and test edge cases. Duration: 3 days."
            ]),
            ("2. Risk Analysis & Mitigation", [
                "• **Risk 1: Missing ffmpeg Dependency on Target Windows Machine**",
                "  *Impact*: High. Brakes Whisper's default file loader.",
                "  *Mitigation*: Bypassed ffmpeg by using Librosa to read audio files directly and passing pre-processed numpy arrays to Whisper's transcribe function.",
                "• **Risk 2: Model Loading Latency**",
                "  *Impact*: Medium. Reloading heavy models on every click breaks UI responsiveness.",
                "  *Mitigation*: Wrapped model loading in Streamlit's `@st.cache_resource` caching wrapper."
            ])
        ]
    )

    # ==================== 5. PROJECT DEVELOPMENT PHASE ====================
    create_professional_pdf(
        "5. Project Development Phase/Project Development Report.pdf",
        "Project Development & Implementation Report",
        "Technical Development Log, Setup Chronicles, and Refactoring Steps",
        [
            ("1. Environment & Setup Chronicles", [
                "Development was initiated individually by setting up a Python virtual environment (`env`) under the project parent directory. Required libraries were installed via `pip` including PyTorch, Sentence-Transformers, Whisper, Librosa, Streamlit, and ReportLab. The code was structured modularly to isolate the UI, database connection, and individual intelligence modules."
            ]),
            ("2. Code Refactoring & Troubleshooting", [
                "During development, two major technical hurdles were resolved:",
                "1. **The ffmpeg Dependency Issue**: Initial testing of Whisper threw a `FileNotFoundError` because Whisper's internal loader calls `ffmpeg` via a subprocess. We refactored `modules/transcription.py` to use `librosa.load(audio_path, sr=16000, mono=True)` which reads files natively, completely bypassing Whisper's ffmpeg dependency.",
                "2. **ReportLab Unicode Rendering Crashes**: Emojis (like sparkles, thumbs-up, warning icons) used in feedback notes crashed ReportLab's standard Helvetica font. We implemented a custom `strip_emojis(text)` helper in `modules/report_generator.py` to clean all inputs before compiling the PDF."
            ]),
            ("3. Relational Schema Mapping", [
                "We constructed `database.py` utilizing SQLAlchemy's declarative base models. We wrote context-managed database sessions (`get_db()`) to prevent resource leaks and automatically seed default target concepts."
            ])
        ]
    )

    # ==================== 6. PROJECT TESTING ====================
    create_professional_pdf(
        "6.Project Testing/Test Plan and Results.pdf",
        "Project Test Plan & Validation Report",
        "Unit Tests, Verification Results, and Performance Latency Analysis",
        [
            ("1. Testing Strategy", [
                "The testing strategy involved two phases: Unit Testing of separate modules using mock data, and End-to-End Testing of the pipeline (Audio Input → Transcription → Semantic Similarity → Feature Extraction → Grading → PDF generation)."
            ]),
            ("2. Performance Benchmark Metrics", [
                "We executed an automated benchmark script (`benchmark_performance.py`) inside the project environment. Results show severe latency reduction due to caching:",
                "• **Whisper Transcription**: Decoded a 33-second WAV recording in `5.11s` during initial model load, and in `1.26s` on subsequent runs.",
                "• **Sentence-BERT Semantic Matching**: Took `11.89s` during the cold cache run (due to model loading), and dropped to **`0.0288s`** during warm cache runs.",
                "• **Librosa Acoustic Features**: Extracted RMS volume, duration, and pause statistics in `1.29s` for a long audio file, and in `0.004s` for a short file."
            ]),
            ("3. Robustness & Edge Cases Tested", [
                "• **Silent Recordings**: Successfully caught by the system, outputting 0 words and showing a warning to prevent database contamination.",
                "• **Long Audio Inputs**: Handled cleanly by Librosa resampling and Whisper decoding without memory leaks or execution timeouts.",
                "• **Encoding Failures**: Emoji character safety was verified by checking that the PDF report generates without crashes."
            ])
        ]
    )

    # ==================== 7. PROJECT DOCUMENTATION ====================
    create_professional_pdf(
        "7.Project Documentation/User Manual and API Docs.pdf",
        "VBCUA User Manual & System Operator Guide",
        "Step-by-Step Guide to Executing, Configuring, and Operating VBCUA",
        [
            ("1. Local Execution Guide", [
                "To launch the application locally:",
                "1. Open a terminal in the project root directory.",
                "2. Activate your Python virtual environment.",
                "3. Execute the Streamlit command: `streamlit run app.py`.",
                "4. Access the local port in your browser: `http://localhost:8501`."
            ]),
            ("2. Functional Interface Walkthrough", [
                "• **Evaluation Tab**: Select your target concept from the pre-populated dropdown, upload a WAV/MP3 audio recording, review the analysis dashboard, and download the PDF report.",
                "• **Concepts Tab**: Manage the SQLite reference database. Add a new concept by typing its title and reference explanation text.",
                "• **History Tab**: Access previous evaluations, view detailed metrics and side-by-side text comparisons, download past PDF reports, or delete past runs (CRUD)."
            ]),
            ("3. Administrator Configurations", [
                "In the sidebar, administrators can adjust the Whisper model size (tiny, base, small) and set the Librosa silence threshold (dB) depending on background noise levels."
            ])
        ]
    )

    # ==================== 8. PROJECT DEMONSTRATION ====================
    # 8.1 Communication
    create_professional_pdf(
        "8.Project Demonstration/Communication.pdf",
        "Presentation & Communication Guide",
        "Demo Delivery Strategy & Structure for Project Showcase",
        [
            ("1. Key Communication Strategy", [
                "The presentation must explain the educational value of evaluating spoken responses. By assessing how students explain concepts in their own words, we measure deep understanding. The demonstration should highlight the transition from raw audio data to structured semantic scoring, speech pacing, and volume analysis, concluding with a downloadable PDF report."
            ]),
            ("2. Presentation Agenda", [
                "1. **The Problem**: Manual grading of audio explanations is time-consuming and subjective.",
                "2. **The Architecture**: Local speech transcribing, Sentence-BERT semantic similarity, acoustic feature extraction, and SQLite database storage.",
                "3. **Live Demonstration**: Upload an audio explanation and review overall scores, pacing analysis, and side-by-side content comparisons.",
                "4. **PDF Output**: Open the compiled PDF report, showcasing the professional print layout."
            ])
        ]
    )

    # 8.2 Demonstration of Proposed Features
    create_professional_pdf(
        "8.Project Demonstration/Demonstration of Proposed Features.pdf",
        "Demonstration of Proposed Features",
        "Interactive Feature Validation Guide",
        [
            ("1. Features to Showcase", [
                "• **Target Concept Preview**: Displays selected reference concepts from SQLite with dynamic definition previews.",
                "• **Interactive Audio Player**: Allows playback of uploaded student responses.",
                "• **Four-Column Scoring Dashboard**: Displays Overall Score, Semantic Similarity %, Silence %, and Fluency Ratio in custom cards.",
                "• **Side-by-Side Content Comparison**: Compares candidate transcription with the reference concept side-by-side.",
                "• **Historical Database CRUD**: Demonstrates full database CRUD functionality (view, download, delete past runs)."
            ])
        ]
    )

    # 8.3 Project Demo Planning
    create_professional_pdf(
        "8.Project Demonstration/Project Demo Planning.pdf",
        "Project Demonstration Script & Plan",
        "Detailed Demo Step-by-Step Script",
        [
            ("1. Step-by-Step Demo Script", [
                "1. **Concept Selection**: Select 'Newton's First Law of Motion' from the dropdown and preview the reference text.",
                "2. **Audio Upload**: Upload `15b1b2c9697a4339b31379b2956af4b9_OSR_us_000_0010_8k.wav`.",
                "3. **Analysis Execution**: Click 'Analyze Response'. The progress spinner updates through transcribing, similarity matching, acoustic analysis, and PDF generation.",
                "4. **Dashboard Review**: Review the metrics, diagnostic notes, and side-by-side text comparisons.",
                "5. **Report Download**: Click the download button and open the PDF report.",
                "6. **CRUD Check**: Navigate to the History tab, verify the run is logged, and delete a past record to verify database integration."
            ])
        ]
    )

    # 8.4 Scalability
    create_professional_pdf(
        "8.Project Demonstration/Scalability.pdf",
        "System Scalability & Future Scope",
        "Long-term Architecture Enhancements",
        [
            ("1. Future Scalability Areas", [
                "• **Multilingual Analysis**: Leverage Whisper's multilingual decoding capabilities to grade student explanations in multiple languages.",
                "• **LMS Integrations**: Package VBCUA as a standard LTI (Learning Tools Interoperability) module for integration into Learning Management Systems (Moodle, Canvas).",
                "• **Cloud Deployment**: Containerize the system using Docker and deploy to AWS ECS/Fargate. Use AWS Aurora Serverless PostgreSQL and cache model weights in a shared Amazon EFS volume."
            ])
        ]
    )

    # 8.5 Team Involvement (Individual Project)
    meta_cols = [100, 404]
    meta_data = [
        ["Date", "15 March 2024"],
        ["Team ID", "IND-VBCUA-01 (Individual Project)"],
        ["Project Name", "Voice-Based Concept Understanding Analyser (VBCUA)"],
        ["Maximum Marks", "1 Mark"]
    ]
    
    involve_cols = [30, 90, 80, 100, 154, 50]
    involve_data = [
        ["S.No", "Team Member Name", "Role in Demo", "Section Presented", "Contribution Summary", "Participation (Active / Passive)"],
        ["1", "Sujan Prasad", "Sole Developer & Presenter", "End-to-End System (Database, AI modules, PDF Report, Streamlit UI)", "Designed, coded, tested and demonstrated the entire VBCUA application individually.", "Active"]
    ]
    
    coord_cols = [200, 304]
    coord_data = [
        ["Aspect", "Details"],
        ["Team Leader / Coordinator", "Sujan Prasad (Sole Developer)"],
        ["Overall Team Coordination Rating (1-5)", "5/5 (Not applicable - Individual Project)"],
        ["Any issues during demo", "None. The application successfully transcribed and graded the verbal response, generating the PDF report instantly."],
        ["How issues were resolved", "Pre-configured SQLite schema and cached the AI model weights locally to ensure zero runtime model download delays during demonstration."]
    ]
    
    create_professional_pdf(
        "8.Project Demonstration/Team Involvement in Demonstration.pdf",
        "Team Involvement in Demonstration",
        "Academic Document detailing Individual Project Execution",
        [
            ("Team Involvement Overview", [
                "This document records the active participation and roles during the project demonstration. Since this project was completed individually, all responsibilities (database design, logic modules, presentation styling, testing, and deployment) were handled solely by Sujan Prasad."
            ])
        ],
        table_blocks=[
            ("", meta_data, meta_cols, False),
            ("Team Demonstration Details:", involve_data, involve_cols, True),
            ("Team Coordination Notes:", coord_data, coord_cols, True)
        ]
    )

if __name__ == "__main__":
    main()
