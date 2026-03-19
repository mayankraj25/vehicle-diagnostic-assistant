# Creta Assistant — OBD-II Intelligent Voice Diagnostic System

A real-time vehicle health monitoring system for the Hyundai Creta
built on a RAG + LLM architecture running entirely locally on Apple Silicon.

## What It Does

Connects to the Creta's OBD-II port via Bluetooth, reads live engine
telemetry, processes it through a deterministic middleware layer, stores
health events in a FAISS vector database, and answers driver questions
in natural spoken language using a locally hosted LLM.

## Architecture
```
Microphone → Whisper STT → Middleware → FAISS RAG → Mistral LLM → TTS → Speaker
```

## Tech Stack

- **Speech Recognition** — faster-whisper (base.en)
- **LLM** — Mistral 7B via Ollama (runs locally, no API key needed)
- **Vector Search** — FAISS-CPU with sentence-transformers
- **TTS** — pyttsx3 (Apple NSSpeechSynthesizer)
- **OBD Interface** — python-obd + Vgate iCar Pro BLE 4.0

## Hardware

- MacBook M3 Air (development)
- Hyundai Creta (2020+)
- Vgate iCar Pro BLE 4.0 OBD dongle

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull mistral
python demo.py
```

## Project Status

- [x] Day 1 — Environment setup and simulated data
- [x] Day 2 — Middleware and threshold detection
- [x] Day 3 — FAISS knowledge base
- [x] Day 4 — LLM engine
- [x] Day 5 — Voice input and output
- [ ] Day 6 — DTC knowledge base
- [ ] Day 7 — Full pipeline integration
- [ ] Live OBD connection (dongle arriving next week)

## Related Project

This is a companion project to PoC-5 — Hybrid LLM Framework for
Time-Series Driven Vehicle Communication, developed at SRMIST for
the Renault Group research programme.
