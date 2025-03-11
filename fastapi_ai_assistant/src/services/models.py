MODELS = ["llama3.2:3b", "llama3"]


def get_model_by_index(index: int) -> str:
    """Gets model name from the list."""
    try:
        language = MODELS[index]
    except IndexError:
        language = MODELS[0]

    return language
