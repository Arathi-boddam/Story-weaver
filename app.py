import streamlit as st
from difflib import SequenceMatcher
from html import escape
import io
import re
import speech_recognition as sr
from story_engine import (
    rewrite_story_with_user_input,
    rewrite_story_with_choice,
    generate_structured_choices
)
from llm import call_llm
from prompts import build_start_prompt, build_continue_prompt

st.set_page_config(page_title="AI Story Weaver", layout="wide")

st.markdown("""
<style>
:root {
  --paper: #f6efe4;
  --paper-2: #fffaf2;
  --ink: #2f2941;
  --muted: #6e6781;
  --accent: #157a6e;
  --accent-2: #d98f39;
  --line: rgba(47, 41, 65, 0.10);
  --shadow: 0 18px 40px rgba(47, 41, 65, 0.08);
}

.stApp {
  background:
    radial-gradient(circle at 12% 10%, rgba(217,143,57,0.16), transparent 22%),
    radial-gradient(circle at 88% 18%, rgba(21,122,110,0.14), transparent 24%),
    linear-gradient(180deg, #fff9f0 0%, var(--paper) 55%, #f1e7d8 100%);
  color: var(--ink);
}

.block-container {
  max-width: 1220px;
  padding-top: 2rem;
  padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #241f34 0%, #171422 100%);
  border-right: 1px solid rgba(255,255,255,0.05);
}

section[data-testid="stSidebar"] * {
  color: #f6f1e8 !important;
}

[data-testid="stTextInputRoot"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
  background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(252,247,239,0.86) 100%) !important;
  border: 1px solid var(--line) !important;
  border-radius: 18px !important;
  color: var(--ink) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.8), 0 8px 18px rgba(47, 41, 65, 0.04) !important;
}

[data-testid="stTextInputRoot"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border: 1px solid rgba(21,122,110,0.28) !important;
  box-shadow: 0 0 0 4px rgba(21,122,110,0.12) !important;
}

.stButton button, [data-testid="stDownloadButton"] button {
  background: linear-gradient(135deg, #1b8c7d 0%, #136b66 100%) !important;
  color: #fffdf9 !important;
  border: none !important;
  border-radius: 999px !important;
  font-weight: 600 !important;
  box-shadow: 0 12px 24px rgba(21,122,110,0.20) !important;
}

.stButton button:hover, [data-testid="stDownloadButton"] button:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(21,122,110,0.25) !important;
}

.hero {
  background:
    radial-gradient(circle at top left, rgba(217,143,57,0.20), transparent 20%),
    radial-gradient(circle at bottom right, rgba(21,122,110,0.18), transparent 24%),
    linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(252,245,234,0.90) 100%);
  padding: 56px 28px;
  border-radius: 28px;
  text-align: center;
  margin-bottom: 28px;
  border: 1px solid rgba(47, 41, 65, 0.08);
  box-shadow: var(--shadow);
}

.hero h1 {
  font-size: 62px;
  color: var(--ink);
  margin-bottom: 14px;
  font-weight: 800;
  letter-spacing: -0.05em;
}

.hero p {
  font-size: 19px;
  color: var(--muted);
  max-width: 760px;
  margin: 0 auto;
  line-height: 1.7;
}

.panel-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.86) 0%, rgba(250,243,234,0.80) 100%);
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 18px;
  box-shadow: var(--shadow);
  margin-bottom: 18px;
}

.section-title {
  color: var(--ink);
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.section-note {
  color: var(--muted);
  font-size: 0.95rem;
  margin-bottom: 0.9rem;
}

.story-card {
  background:
    linear-gradient(180deg, rgba(255,255,255,0.90) 0%, rgba(252,247,240,0.84) 100%);
  padding: 18px;
  border-radius: 22px;
  margin-bottom: 14px;
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}

.preview-card {
  background: rgba(21,122,110,0.08);
  border: 1px dashed rgba(21,122,110,0.26);
  color: var(--ink);
  border-radius: 18px;
  padding: 12px 14px;
  margin-top: 8px;
}

.voice-box summary {
  color: var(--accent);
  font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


def _highlight_html(action_type=None):
    colors = {
        "user": "#fff3a3",
        "ai": "#cce5ff",
        "twist": "#e0ccff",
        "dark": "#d6d6d6",
        "character": "#ccffd8",
        "choice": "#ffd6cc",
    }

    color = colors.get(action_type, "#fff3a3")

    return (
        f"<span style='background-color:{color}; color:#1f1f1f; padding:0.1rem 0.25rem; "
        "border-radius:0.25rem; font-weight:600;'>"
    )


def get_story_rules():
    rules = [
        f"Genre must stay consistent: {st.session_state.genre}",
        "Characters and plot should remain coherent across rewrites",
        f"Narrative voice: {style}",
        "Your added or chosen contribution should be integrated naturally",
    ]
    if "control_action" in st.session_state:
        rules.append(f"Active story control: {st.session_state.control_action}")
    return rules


def parse_choices(raw_choices):
    parsed = []
    for line in raw_choices.splitlines():
        choice = line.strip()
        if not choice:
            continue
        if len(choice) > 2 and choice[0].isdigit() and choice[1] == ".":
            choice = choice[2:].strip()
        parsed.append(choice)
    return parsed


def get_story_text():
    return "\n\n".join([item["text"] for item in st.session_state.story])


def generate_visual_prompt(text):
    return f"Create a cinematic illustration of: {text[:300]}"

def remix_genre(story, current_genre, temperature):
    new_genre = "Sci-Fi" if current_genre != "Sci-Fi" else "Fantasy"
    prompt = f"Rewrite this story in {new_genre} genre but keep plot same:\n\n{story}"
    return call_llm(prompt, temperature), new_genre


def extract_character_names(text):
    blacklist = {
        "The", "A", "An", "And", "But", "Or", "If", "Then", "When", "While",
        "He", "She", "They", "His", "Her", "Their", "I", "We", "You",
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        "January", "February", "March", "April", "May", "June", "July", "August",
        "September", "October", "November", "December",
        "This", "That", "These", "Those",
        "As", "With", "In", "On", "At", "By", "From", "Into", "Over",
    }

    counts = {}

    matches = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", text)

    for match in matches:
        words = match.split()

        if len(words) > 1:
            continue

        word = words[0]

        if word in blacklist:
            continue

        
        counts[word] = counts.get(word, 0) + 1

    filtered = [
        name for name, count in counts.items()
        if count >= 2
    ]

    return sorted(filtered, key=lambda x: (-counts[x], x))[:8]


def is_llm_error(response_text):
    return isinstance(response_text, str) and response_text.startswith("Error:")


def transcribe_audio(uploaded_audio):
    if uploaded_audio is None:
        return None, None

    recognizer = sr.Recognizer()
    audio_bytes = io.BytesIO(uploaded_audio.getvalue())

    try:
        with sr.AudioFile(audio_bytes) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data), None
    except sr.UnknownValueError:
        return None, "Voice input could not be understood clearly."
    except sr.RequestError as exc:
        return None, f"Speech recognition service failed: {exc}"
    except Exception as exc:
        return None, f"Voice input failed: {exc}"


def render_voice_field(field_key, label, widget_type="text_area", height=None):
    st.markdown(f"**{label}**")

    
    if widget_type == "text_input":
        st.text_input(label, key=field_key, label_visibility="collapsed")
    else:
        st.text_area(label, key=field_key, height=height, label_visibility="collapsed")

    # Mic directly below but visually tied
    with st.expander("🎤 Speak instead", expanded=False):
        st.caption(f"Speak to fill {label.lower()}")
        voice_audio = st.audio_input(
            "Record voice",
            key=f"{field_key}_audio",
            label_visibility="collapsed",
        )

        if voice_audio is not None:
            transcript, voice_error = transcribe_audio(voice_audio)

            if voice_error:
                st.session_state.error_message = voice_error

            elif transcript:
                pending_key = f"{field_key}_pending_voice"
                current_value = st.session_state.get(field_key, "").strip()

                if widget_type == "text_area" and current_value:
                    st.session_state[pending_key] = f"{current_value}\n{transcript}"
                else:
                    st.session_state[pending_key] = transcript

                st.session_state.error_message = None
                st.rerun()


def _inject_diff_highlights(old_text, new_text):
    if not old_text or "[HIGHLIGHT]" in new_text:
        return new_text

    matcher = SequenceMatcher(None, old_text, new_text)
    parts = []
    highlighted = False

    for tag, _, _, j1, j2 in matcher.get_opcodes():
        segment = new_text[j1:j2]
        if not segment:
            continue
        if tag in {"insert", "replace"} and segment.strip():
            parts.append(f"[HIGHLIGHT]{segment}[/HIGHLIGHT]")
            highlighted = True
        else:
            parts.append(segment)

    if not highlighted:
        return new_text

    return "".join(parts)


def _apply_fallback_highlight(text, fallback_text):
    if not fallback_text or "[HIGHLIGHT]" in text:
        return text

    snippet = fallback_text.strip()
    if not snippet:
        return text

    lower_text = text.lower()
    lower_snippet = snippet.lower()
    start = lower_text.find(lower_snippet)
    if start == -1:
        return text

    end = start + len(snippet)
    return text[:start] + "[HIGHLIGHT]" + text[start:end] + "[/HIGHLIGHT]" + text[end:]


def render_story_text(text, action_type=None, fallback_text=None):
    if "[HIGHLIGHT]" not in text and fallback_text:
        text = _apply_fallback_highlight(text, fallback_text)

    safe_text = escape(text)
    safe_text = safe_text.replace("[HIGHLIGHT]", _highlight_html(action_type))
    safe_text = safe_text.replace("[/HIGHLIGHT]", "</span>")
    safe_text = safe_text.replace("\n", "<br>")
    return safe_text


if "story" not in st.session_state:
    st.session_state.story = []
    st.session_state.started = False
if "error_message" not in st.session_state:
    st.session_state.error_message = None
if "title_input" not in st.session_state:
    st.session_state.title_input = ""
if "hook_input" not in st.session_state:
    st.session_state.hook_input = ""
if "user_input_text" not in st.session_state:
    st.session_state.user_input_text = ""
if "title_input_pending_voice" not in st.session_state:
    st.session_state.title_input_pending_voice = None
if "hook_input_pending_voice" not in st.session_state:
    st.session_state.hook_input_pending_voice = None
if "user_input_text_pending_voice" not in st.session_state:
    st.session_state.user_input_text_pending_voice = None

for field_key in ["title_input", "hook_input", "user_input_text"]:
    pending_key = f"{field_key}_pending_voice"
    if st.session_state.get(pending_key) is not None:
        st.session_state[field_key] = st.session_state[pending_key]
        st.session_state[pending_key] = None


def consume_control_action():
    action = st.session_state.get("control_action")
    if action:
        del st.session_state.control_action
    if "current_control_type" in st.session_state:
        del st.session_state.current_control_type
    return action


st.sidebar.title("⚙️ Controls")
temperature = st.sidebar.slider(
    "🎨 Creativity (Controls randomness & imagination)",
    0.0, 1.0, 0.7
)
st.sidebar.markdown("### Narrative Voice")
st.sidebar.caption("Choose the tone the storyteller should lean into on each rewrite.")
style = st.sidebar.selectbox(
    "Select a writing mood",
    ["Cinematic", "Descriptive", "Minimal", "Dramatic"],
    help="This affects how the AI phrases scenes, pacing, and emotional intensity.",
)
st.sidebar.markdown("### 🎯 Story Controls")

if st.sidebar.button("Add Twist"):
    st.session_state.control_action = "Add a surprising plot twist"
    st.session_state.current_control_type = "twist"

if st.sidebar.button("Make Darker"):
    st.session_state.control_action = "Make the story darker and more intense"
    st.session_state.current_control_type = "dark"

if st.sidebar.button("Introduce Character"):
    st.session_state.control_action = "Introduce a new important character"
    st.session_state.current_control_type = "character"


if not st.session_state.started:
    st.markdown("""
<div class="hero">
    <h1>🧵 AI Story Weaver</h1>
    <p>
        Build interactive stories with guided rewrites, voice input, branching choices,
        and creative controls that keep the narrative coherent.
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Start a New Story</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Set the premise, mood, and genre before the first scene is written.</div>', unsafe_allow_html=True)
    render_voice_field("title_input", "Story Title", widget_type="text_input")
    genre = st.selectbox("Genre", ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Comedy"])
    render_voice_field("hook_input", "Initial Hook / Setting", height=120)

    if st.button("Start the Story"):
        title = st.session_state.title_input.strip()
        hook = st.session_state.hook_input.strip()
        if title and hook:
            with st.spinner("Generating..."):
                prompt = build_start_prompt(title, genre, hook)
                response = call_llm(prompt, temperature)
                if is_llm_error(response):
                    st.session_state.error_message = f"Start Story failed. {response}"
                    st.rerun()

                st.session_state.story = [{"type": "ai", "text": response, "action": "ai"}]
                st.session_state.genre = genre
                st.session_state.started = True
                st.session_state.error_message = None
                st.session_state.user_input_text = ""
                st.rerun()
        else:
            st.warning("Fill all fields")
    st.markdown('</div>', unsafe_allow_html=True)


else:
    full_story_text = get_story_text()

    st.markdown(
        f"""
        <div class="hero" style="padding:32px 26px; text-align:left;">
            <h1 style="font-size:44px; margin-bottom:8px;">📖 Your Story</h1>
            <p style="margin:0;">Current genre: <strong>{escape(st.session_state.genre)}</strong>. Guide the story with controls, your own edits, or voice input.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
    if "control_action" in st.session_state:
        st.info(f"Active control: {st.session_state.control_action}")
    st.caption("Highlighted text marks the part added from your input or selected choice.")
    with st.expander("📜 Story Rules (AI follows these)", expanded=True):
        st.caption("These rules guide the AI to maintain consistency and narrative quality.")
        st.markdown("\n".join([f"• {rule}" for rule in get_story_rules()]))
    with st.expander("Character Tracker", expanded=False):
        characters = extract_character_names(full_story_text)
        if characters:
            for character in characters:
                st.markdown(f"- {character}")
        else:
            st.caption("No recurring characters detected yet.")
    md_story = "\n\n".join([f"{item['text']}" for item in st.session_state.story])
    st.download_button(
        "📥 Export as Markdown",
        data=md_story,
        file_name="story.md",
        mime="text/markdown",
    )

   
    for item in st.session_state.story:
        st.markdown(
            f"""
            <div class='story-card'>
                {render_story_text(item['text'], item.get('action'))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Story Controls</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Remix the narrative, derive a visual prompt, or revert a recent turn.</div>', unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("🎭 Genre Remix"):
            with st.spinner("🔀 Remixing genre..."):
                full_story = get_story_text()
                remixed, new_genre = remix_genre(full_story, st.session_state.genre, temperature)
                if not is_llm_error(remixed):
                    st.session_state.story = [{"type": "ai", "text": remixed, "action": "ai"}]
                    st.session_state.genre = new_genre
                    st.rerun()

    with colB:
        if st.button("🖼️ Visualize Scene"):
            latest = st.session_state.story[-1]["text"]
            visual = generate_visual_prompt(latest)
            st.info(visual)

    with colC:
        if st.button("↩️ Undo Last Turn"):
            if len(st.session_state.story) > 1:
                st.session_state.story.pop()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Add Your Part</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Type your next scene or use voice to inject a new beat into the story.</div>', unsafe_allow_html=True)
    render_voice_field("user_input_text", "Add your part", height=140)

    if st.session_state.user_input_text:
        st.caption("✨ Live preview of your addition:")
        st.markdown(f"""
        <div class="preview-card" style="opacity:0.92; font-style:italic;">
            👉 {st.session_state.user_input_text}
        </div>
        """, unsafe_allow_html=True)

    if st.button("Add My Part"):
        user_input = st.session_state.user_input_text.strip()
        if user_input:
            with st.spinner("🔮 Rewriting timeline..."):
                previous_story = "\n".join([s["text"] for s in st.session_state.story])
                action_type = st.session_state.get("current_control_type", "user")
                control_action = consume_control_action()
                updated = rewrite_story_with_user_input(
                    st.session_state.story,
                    st.session_state.genre,
                    user_input,
                    style,
                    temperature,
                    control_action,
                )
                if is_llm_error(updated):
                    st.warning("Retrying...")
                    updated = rewrite_story_with_user_input(
                        st.session_state.story,
                        st.session_state.genre,
                        user_input,
                        style,
                        temperature,
                        control_action,
                    )
                    if is_llm_error(updated):
                        st.session_state.error_message = f"Add My Part failed. {updated}"
                        st.rerun()
                updated = _inject_diff_highlights(previous_story, updated)
                updated = _apply_fallback_highlight(updated, user_input)
                st.session_state.story = [{"type": "ai", "text": updated, "action": action_type}]
                st.session_state.error_message = None
                st.session_state.user_input_text = ""
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    
    with col1:
        if st.button("✨ Continue with AI"):
            with st.spinner("🧠 Expanding narrative..."):
                full_story = "\n".join([s["text"] for s in st.session_state.story])

                extra_instruction = f"Write in {style.lower()} style."
                control_action = consume_control_action()

                if control_action:
                    extra_instruction += " " + control_action

                prompt = build_continue_prompt(
                    st.session_state.genre,
                    full_story + "\n" + extra_instruction
                )

                response = call_llm(prompt, temperature)
                if is_llm_error(response):
                    st.warning("Retrying...")
                    response = call_llm(prompt, temperature)
                    if is_llm_error(response):
                        st.session_state.error_message = f"Continue with AI failed. {response}"
                        st.rerun()

                st.session_state.story.append({
                    "type": "ai",
                    "text": response,
                    "action": "ai"
                })
                st.session_state.error_message = None
                st.rerun()

    
    with col2:
        if st.button("🔀 Give Me Choices"):
            with st.spinner("⚡ Generating possibilities..."):
                choices = generate_structured_choices(
                    st.session_state.story,
                    st.session_state.genre,
                    temperature,
                    st.session_state.get("control_action"),
                )
                if is_llm_error(choices):
                    st.warning("Retrying...")
                    choices = generate_structured_choices(
                        st.session_state.story,
                        st.session_state.genre,
                        temperature,
                        st.session_state.get("control_action"),
                    )
                    if is_llm_error(choices):
                        st.session_state.error_message = f"Give Me Choices failed. {choices}"
                        st.rerun()
                st.session_state.choices = choices
                st.session_state.error_message = None

    
    if "choices" in st.session_state:
        st.subheader("Choose a direction:")
        parsed_choices = parse_choices(st.session_state.choices)
        if parsed_choices:
            for index, selected in enumerate(parsed_choices):
                if st.button(selected, key=f"choice_{index}"):
                    with st.spinner("🧩 Rewriting with your choice..."):
                        previous_story = "\n".join([s["text"] for s in st.session_state.story])
                        control_action = consume_control_action()
                        updated = rewrite_story_with_choice(
                            st.session_state.story,
                            st.session_state.genre,
                            selected,
                            style,
                            temperature,
                            control_action,
                        )
                        if is_llm_error(updated):
                            st.warning("Retrying...")
                            updated = rewrite_story_with_choice(
                                st.session_state.story,
                                st.session_state.genre,
                                selected,
                                style,
                                temperature,
                                control_action,
                            )
                            if is_llm_error(updated):
                                st.session_state.error_message = f"Continue with Choice failed. {updated}"
                                st.rerun()

                        updated = _inject_diff_highlights(previous_story, updated)
                        updated = _apply_fallback_highlight(updated, selected)
                        action_type = st.session_state.get("current_control_type", "choice")
                        st.session_state.story = [{"type": "ai", "text": updated, "action": action_type}]
                        st.session_state.error_message = None
                        del st.session_state.choices
                        st.rerun()
        else:
            st.text(st.session_state.choices)

   
    if st.button("🔄 Reset"):
        st.session_state.clear()
        st.rerun()
