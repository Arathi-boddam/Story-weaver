def get_full_story(story_list):
    return "\n".join(story_list)


def add_to_story(story_list, new_text):
    story_list.append(new_text)
    return story_list
