# Phase 1: Brainstorming & Ideation

This folder contains the conceptualization documents for the Voice-Based Concept Understanding Analyser (VBCUA). It maps user empathy, identifies core personas, defines target pain points, and establishes the initial design thinking framework.

---

## 👥 Empathy Map

### 1. Executive Summary
Understanding how candidates formulate and deliver conceptual explanations is vital for automated education grading systems. The Voice-Based Concept Understanding Analyser (VBCUA) target persona maps to two major user segments:
* **Students**: Who need objective, instant conceptual validation.
* **Instructors**: Who need to assess students' active vocabulary without subjective grading bottlenecks.

### 2. What Users THINK & FEEL
* **Students**: They often think:
  * *"How accurate is this semantic matching engine?"*
  * *"Will my regional accent or a brief stutter lower my score?"*
  * *"I need immediate grading on my explanation so I can fix my conceptual gaps before the final exam."*
* **Instructors**: They feel overwhelmed by manual grading cycles, thinking:
  * *"I spend too many hours listening to audio recordings manually."*
  * *"I want to know if my students are merely memorizing definitions verbatim or if they understand the actual logical dependencies of the subject matter."*

### 3. What Users SAY & DO
* **Students**: They say: *"I know the topic, but I find it hard to explain it verbally in class."* During verbal assessments, they tend to pause frequently, use filler words (like "um", "uh", "like") when searching for terminology, and actively request structured diagnostics to improve.
* **Instructors**: They say: *"I want to assign more oral exams, but I don't have the time to grade them objectively for 100 students."* They record student explanations, check them against a checklist, and write feedback manually.

### 4. Pains & Gains
* **Pains (Bottlenecks)**: Subjective grading of spoken answers, delayed feedback cycles, lack of clear metrics showing speech fluency or vocal confidence, and high anxiety during verbal exams.
* **Gains (Value Delivered)**: Instant objective grading, transparent feedback on filler word counts and pause ratios, side-by-side text comparisons, and structured, actionable diagnostic notes showing clear areas of conceptual improvement.

---

## 💡 Project Conception Report

### 1. Project Background & Initiation
In modern education, assessing conceptual understanding via verbal communication is key. However, manual grading of spoken explanations is time-consuming and subjective. The Voice-Based Concept Understanding Analyser (VBCUA) was conceived to automate this process locally, privately, and securely.

### 2. User Personas & Empathy Map Details
* **Student Persona**: Needs immediate feedback on oral explanations, worries about grading bias, and wants actionable metrics to improve speech fluency.
* **Instructor Persona**: Manages large classes, spends excessive hours listening to audio recordings, and seeks an objective helper to check semantic concept matching and speech pacing.

### 3. Brainstorming & Ideation Phase
During the ideation phase, various architectural approaches were evaluated. The team decided on a local-first AI system combining OpenAI Whisper for transcription, Sentence-BERT for semantic similarity matching, and Librosa for extracting acoustic characteristics (volume and silence pauses). This avoids external API costs and secures user privacy.

### 4. Problem-Solution Fit
The fit is achieved by mapping the candidate's spoken text directly to stored reference concepts in a local relational database, calculating a combined content-delivery score, and generating a professional, downloadable feedback report in PDF format.
