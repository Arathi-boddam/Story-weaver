from llm import call_llm


def _has_highlight_markers(text):
    return "[HIGHLIGHT]" in text and "[/HIGHLIGHT]" in text


def _highlight_is_near_end(text):
    start = text.find("[HIGHLIGHT]")
    if start == -1:
        return False
    return start > len(text) * 0.7


def _rewrite_story(full_story, addition, style, temperature, label, control_action=None):
    control_instruction = ""
    if control_action:
        control_instruction = f"\n- Also apply this story control: {control_action}"

    prompt = f"""
You are an expert storyteller and editor.

Here is the story so far:
{full_story}

The user wants to add this:
"{addition}"

Task:
- Rewrite the FULL story so the new material is woven into the most suitable existing moment.
- Prefer inserting it into the middle or earlier parts of the story when that improves logic, pacing, or character flow.
- Do not place it as a final appended paragraph unless the story structure makes that absolutely necessary.

Rules:
- Maintain narrative flow
- Keep character consistency
- Modify earlier parts if needed
- Write in {style.lower()} style
- Use this {label} material meaningfully, not superficially
- Preserve the core wording of the added material closely enough that it is still recognizable
- Wrap only the newly integrated {label} text with [HIGHLIGHT] and [/HIGHLIGHT]
- Keep the rest of the story outside those tags
- If a story control is provided, incorporate it into the rewrite naturally
- Do not mention instructions or control labels explicitly in the story
- Return only the full updated story
{control_instruction}
"""
    result = call_llm(prompt, temperature)
    if _has_highlight_markers(result) and not _highlight_is_near_end(result):
        return result

    retry_prompt = f"""
The previous response did not place the highlight correctly.

Rewrite the FULL story again and move the highlighted text to a more suitable earlier or middle location.

Story so far:
{full_story}

Required material:
"{addition}"

Rules:
- You must include [HIGHLIGHT] and [/HIGHLIGHT] markers exactly once around the inserted material
- The [HIGHLIGHT]...[/HIGHLIGHT] section must appear before the final 30% of the story unless impossible
- Integrate it naturally into an existing scene, transition, or turning point
- Do not add an ending-only add-on
- Write in {style.lower()} style
- Preserve the core wording of this material so it remains recognizable
- Apply this story control naturally if provided: {control_action or "None"}
- Return only the full updated story
"""
    return call_llm(retry_prompt, temperature)


def rewrite_story_with_user_input(story, genre, user_input, style, temperature, control_action=None):
    full_story = "\n".join([s["text"] for s in story])
    return _rewrite_story(
        full_story,
        user_input,
        style,
        temperature,
        "user-contributed",
        control_action,
    )


def rewrite_story_with_choice(story, genre, choice, style, temperature, control_action=None):
    full_story = "\n".join([s["text"] for s in story])
    return _rewrite_story(
        full_story,
        choice,
        style,
        temperature,
        "chosen-direction",
        control_action,
    )


def generate_structured_choices(story, genre, temperature, control_action=None):
    full_story = "\n".join([s["text"] for s in story])
    control_instruction = ""
    if control_action:
        control_instruction = f"\nBias the options to reflect this story control: {control_action}"

    prompt = f"""
Story so far:
{full_story}

Generate 3 clear next directions.
{control_instruction}

Format strictly:
1. ...
2. ...
3. ...
"""
    return call_llm(prompt, temperature)
