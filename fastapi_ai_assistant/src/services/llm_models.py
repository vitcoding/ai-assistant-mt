# MODELS = ["gemma3:4b", "gemma3:12b", "llama3.2:3b"]
MODELS = [
    "gemma2:9b",
    "llama3.2:3b",
    # "deepseek-r1:8b",
    # "gemma3:4b",
    # "gemma3:12b",
]


def get_model_by_index(index: int) -> str:
    """Gets model name from the list."""
    try:
        language = MODELS[index]
    except IndexError:
        language = MODELS[0]

    return language
