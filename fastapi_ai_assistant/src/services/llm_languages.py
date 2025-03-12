LANGUAGES = ["Russian", "English"]


def get_langage_by_index(index: int) -> str:
    """Gets language from the list."""
    try:
        language = LANGUAGES[index]
    except IndexError:
        language = LANGUAGES[0]

    return language
