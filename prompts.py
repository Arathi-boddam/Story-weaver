def get_system_prompt():
    return """
You are an expert storyteller.
Stay consistent with characters, plot, and genre.
"""

def build_start_prompt(title, genre, hook):
    return f"{get_system_prompt()}\n\nTitle: {title}\nGenre: {genre}\n{hook}\nStart the story."

def build_continue_prompt(genre, story):
    return f"{get_system_prompt()}\n\nGenre: {genre}\nStory so far:\n{story}\nContinue."

def build_choices_prompt(genre, story):
    return f"{get_system_prompt()}\n\nGenre: {genre}\nStory:\n{story}\nGive 3 next options."
