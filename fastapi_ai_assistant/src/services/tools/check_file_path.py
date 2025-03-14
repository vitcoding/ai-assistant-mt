import os


# draft
def check_path(path: str, is_dir: bool = False):
    current_path = os.path.dirname(os.path.abspath(__file__))

    if is_dir and os.path.isdir(path):
        return True
    elif not is_dir and os.path.isfile(path):
        return True
    return False
