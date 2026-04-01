# AI Story Weaver

AI Story Weaver is a Streamlit app for building interactive stories with AI-assisted continuation, rewrite-based user edits, branching choices, and voice-assisted input.

## Features

- Start a story from a title, genre, and opening hook
- Continue the story with AI
- Add your own text and have it rewritten naturally into the story
- Generate branching choices and continue from a selected path
- Use story controls like `Add Twist`, `Make Darker`, and `Introduce Character`
- Adjust creativity with a temperature slider
- Choose a narrative voice such as `Cinematic`, `Descriptive`, `Minimal`, or `Dramatic`
- Highlight newly integrated user or choice-driven changes
- Track recurring character names
- Export the current story
- Use voice input for title, hook, and story additions

## Tech Stack

- Python
- Streamlit
- Requests
- `streamlit-mic-recorder`
- Local LLM backend via Ollama-style HTTP API

## Project Files

- `app.py` - Streamlit UI and interaction flow
- `llm.py` - LLM request wrapper
- `story_engine.py` - rewrite and choice-generation logic
- `prompts.py` - prompt builders
- `memory.py` - simple story utilities
- `req.txt` - Python dependencies

## Requirements

- Python 3.10+
- A local LLM server running at:

```text
http://localhost:11434/api/generate
```

- A model available to that server, currently referenced in `llm.py`

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r req.txt
```

## Run

```bash
streamlit run app.py
```

## Notes

- The app currently expects a local model endpoint rather than a hosted API.
- Voice input depends on `streamlit-mic-recorder` and browser microphone permissions.
- Highlighting is designed to show the part most recently integrated into the story.
