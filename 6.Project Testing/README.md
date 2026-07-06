# Phase 6: Project Testing

This folder contains the quality assurance verification documents, latency logs, and testing benchmarks for the Voice-Based Concept Understanding Analyser (VBCUA).

---

## 🧪 Project Test Plan & Validation Report

### 1. Testing Strategy
The testing strategy involved two phases: Unit Testing of separate modules using mock data, and End-to-End Testing of the pipeline (Audio Input → Transcription → Semantic Similarity → Feature Extraction → Grading → PDF generation).

### 2. Performance Benchmark Metrics
We executed an automated benchmark script (`benchmark_performance.py`) inside the project environment. Results show severe latency reduction due to resource caching:
* **Whisper Transcription**: Decoded a 33-second WAV recording in `5.11s` during initial model load, and in `1.26s` on subsequent runs.
* **Sentence-BERT Semantic Matching**: Took `11.89s` during the cold cache run (due to model loading), and dropped to **`0.0288s`** during warm cache runs.
* **Librosa Acoustic Features**: Extracted RMS volume, duration, and pause statistics in `1.29s` for a long audio file, and in `0.004s` for a short file.

### 3. Robustness & Edge Cases Tested
* **Silent Recordings**: Successfully caught by the system, outputting 0 words and showing a warning to prevent database contamination.
* **Long Audio Inputs**: Handled cleanly by Librosa resampling and Whisper decoding without memory leaks or execution timeouts.
* **Encoding Failures**: Emoji character safety was verified by checking that the PDF report generates without crashes.
