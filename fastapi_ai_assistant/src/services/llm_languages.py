LANGUAGES = ["Russian", "English"]

LOCALES = {"Russian": "ru_RU.UTF-8", "English": "en_GB.UTF-8"}


def get_langage_by_index(index: int) -> str:
    """Gets language from the list."""
    try:
        language = LANGUAGES[index]
    except IndexError:
        language = LANGUAGES[0]

    return language
