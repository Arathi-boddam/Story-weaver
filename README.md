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

## Memory / Consistency Strategy

The app keeps consistency by always passing the full current story back into the model before every rewrite, continuation, or choice generation. Instead of simply appending user input, the rewrite flow asks the model to integrate new material into the most suitable place in the narrative. This helps preserve character continuity, plot flow, tone, and earlier setup details. Story controls like Add Twist, Make Darker, and Introduce Character are also injected as controlled instructions so changes stay aligned with the existing story.

## Bonus Features Implemented

- Voice input for story title, hook, and user-added story text
- Highlighting of newly integrated user or choice-driven additions
- Character tracker for recurring names in the story
- Export current story as a file
- Branching choice generation with clickable choice selection
- Undo last turn support
- Retry logic with countdown handling for temporary API or rate-limit failures
- Genre remix and scene visualization prompt generation

## One Thing That Did Not Work Well At First

At first, user additions were often being appended to the end of the story instead of being woven naturally into the narrative. I changed the prompting strategy so the model explicitly rewrites the full story and places the new material where it fits best. I also added stronger rewrite rules and highlight logic so inserted content is easier to track.

## What I Would Improve Next With Another Day of Work

With another day, I would improve the structured memory system beyond just passing the full story each time. I would add a dedicated story-state layer that tracks characters, locations, unresolved plot threads, and recent events separately from the raw narrative text. That would make long stories more consistent and reduce drift over multiple turns. I would also improve the UI further by polishing the voice experience and making the story controls feel more interactive and visual.

## Demo

A short walkthrough of the app is available here:

[Watch the demo on Google Drive](https://drive.google.com/drive/folders/1IpK_oyITfhgvC2NeBRx7FIB50aZwG2Gz?usp=sharing)

