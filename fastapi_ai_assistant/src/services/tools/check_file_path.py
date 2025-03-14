import os


def check_path():
    app_path = os.path.dirname(os.path.abspath(__file__))
    print(app_path)

    directory_nltk_data_path = f"{app_path}/.venv/nltk_data"
    directory_punkt_tab_path = (
        f"{directory_nltk_data_path}/tokenizers/punkt_tab"
    )
    if not os.path.isdir(directory_punkt_tab_path):
        print(directory_punkt_tab_path)
