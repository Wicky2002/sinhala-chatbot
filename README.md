# Sinhala Chatbot (Offline, Streamlit + Ollama)

## Final Project Report

This repository contains a Sinhala-focused AI chatbot application built with Streamlit and Ollama.
The assistant is optimized for Sri Lankan university students and professionals, with a strong focus on natural polite spoken Sinhala, contextual quality, and fully local/offline inference.

## Project Summary

The application provides a chat interface that runs a local LLM through Ollama and applies:

- A strict Sinhala language/persona system prompt
- Few-shot in-context examples for response style control
- Real-time token streaming in the UI
- User-adjustable generation controls (temperature, top-p)
- Response quality utilities:
  - Sinhala purity score
  - Post-processing sanitizer for common output artifacts
- Session utilities:
  - Clear conversation
  - Regenerate last answer
  - Download chat history

## Current Implementation

Main file:

- `app.py`: Full Streamlit application (UI, state management, local model inference, metrics, export)

Key modules/functions inside `app.py`:

- `SYSTEM_PROMPT`: Enforces language and grammar behavior
- `HARDCODED_DATASET`: Embedded few-shot dataset (system + examples)
- `get_sinhala_purity(text)`: Calculates Sinhala character purity percentage
- `sanitize_sinhala_output(text)`: Cleans common Sinhala generation artifacts
- `get_chat_download_string()`: Exports session chat history (excluding hidden seed dataset)

## Architecture Overview

1. User enters a prompt in Streamlit chat input.
2. App combines:
   - Permanent seed dataset (`HARDCODED_DATASET`)
   - Most recent user conversation window (`last 4` interactions)
3. App calls `ollama.chat(..., stream=True)` for incremental generation.
4. Streamed response is displayed live.
5. Response is sanitized, scored, and saved with metadata (`speed`, `purity`).
6. Sidebar tools allow clearing, regeneration, and log download.

## Requirements

- Python 3.9+
- Ollama installed and running locally
- Streamlit
- Python Ollama package
- Local model available in Ollama:
  - `Tharusha_Dilhara_Jayadeera/singemma`

## Setup

### 1. Clone and enter project

```powershell
git clone <your-repo-url>
cd sinhala-chatbot
```

### 2. (Recommended) Create virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install streamlit ollama
```

### 4. Ensure Ollama is running and model is available

```powershell
ollama serve
ollama pull Tharusha_Dilhara_Jayadeera/singemma
```

## Run

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in terminal (usually `http://localhost:8501`).

## Usage Notes

- Use sidebar sliders to tune creativity/focus:
  - `Temperature`
  - `Top-P`
- Use `Regenerate Last Response` to retry the latest answer.
- Use `Download Chat Log` to export the active conversation.
- Hidden seed examples are not shown in the UI and are excluded from exports.

## Troubleshooting

If `streamlit run app.py` fails:

1. Verify dependencies are installed:

```powershell
pip show streamlit
pip show ollama
```

2. Verify Ollama is accessible:

```powershell
ollama list
```

3. Confirm model name exists exactly as used in code:

- `Tharusha_Dilhara_Jayadeera/singemma`

4. If PowerShell execution policy blocks venv activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Limitations (Current Version)

- Dataset is hardcoded in source.
- No automated tests yet.
- No dependency lock file yet (`requirements.txt` not included).
- Context window is manually limited (last 4 interactions).

## Suggested Next Improvements

- Add `requirements.txt` (or `pyproject.toml`) for reproducible setup.
- Add basic tests for sanitizer and purity scoring functions.
- Move system prompt and few-shot dataset to external JSON/YAML config.
- Add logging for latency and quality metrics across sessions.
- Add optional multi-model selection from sidebar.

## License

Add your preferred license (MIT, Apache-2.0, etc.).