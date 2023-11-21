import os

from app.person import MePC


def get_abs_path(path):
    return os.path.join(os.getcwd(), 'app/data/icons/404.png')
    if path:
        return os.path.join(MePC().wx_dir, path)
    else:
        return os.path.join(os.getcwd(), 'app/data/icons/404.png')
