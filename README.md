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
- Google Gemini API

## Project Files

- `app.py` - Streamlit UI and interaction flow
- `llm.py` - LLM request wrapper
- `story_engine.py` - rewrite and choice-generation logic
- `prompts.py` - prompt builders
- `memory.py` - simple story utilities
- `req.txt` - Python dependencies

## Requirements

- Python 3.10+
- A valid `GEMINI_API_KEY`

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r req.txt
export GEMINI_API_KEY="your_api_key"
```

## Run

```bash
streamlit run app.py
```

## Notes

- The app currently uses the Gemini API from `llm.py`.
- Voice input depends on `streamlit-mic-recorder` and browser microphone permissions.
- Highlighting is designed to show the part most recently integrated into the story.

## Memory / Consistency Strategy

The app keeps story consistency by always sending the full current story back to the model before every continuation, rewrite, or choice generation step. Instead of appending user input directly, the rewrite flow asks the model to integrate the new content into the most suitable place in the narrative. This helps preserve plot flow, character continuity, pacing, and tone. Story controls such as `Add Twist`, `Make Darker`, and `Introduce Character` are also injected as structured instructions so the model changes the story intentionally instead of randomly.

## Bonus Features Implemented

- Voice input for title, hook, and story additions
- Highlighting of newly integrated user or choice-driven changes
- Character tracker for recurring names
- Export current story
- Branching choices with direct clickable selection
- Undo support for reversing the last AI turn
- Retry behavior for temporary failures or rate-limit-style errors
- Genre remix and scene visualization prompt generation

## One Thing That Did Not Work Well At First

Initially, when the user added their own text, the model often pushed that content to the end of the story instead of placing it where it fit naturally. I changed the prompting strategy so the model rewrites the full story and explicitly integrates the new material into the most suitable earlier or middle point. I also added stronger instructions and highlight handling so the inserted content is easier to trace in the final output.

## What I Would Improve Next

With another day of work, I would improve the memory layer beyond simply resending the full story text each time. I would add a structured story-state system that tracks characters, locations, unresolved threads, and recent events separately from the prose. That would make long-form consistency stronger and reduce drift as the story grows. I would also further refine the UI and voice interaction to make the writing flow feel more seamless.

## Demo

A short walkthrough of the app is available here:

[Watch the demo on Google Drive](https://drive.google.com/drive/folders/1IpK_oyITfhgvC2NeBRx7FIB50aZwG2Gz?usp=sharing)
