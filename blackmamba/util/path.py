#!python3

import os

_DOCUMENTS = os.path.expanduser('~/Documents')


def strip_documents_folder(path):
    """
    Strip ~/Documents part of the path.

    ~/Documents/hallo.py -> hallo.py
    ~/Documents/folder/a.py -> folder/a.py
    """
    if path.startswith(_DOCUMENTS):
        return path[len(_DOCUMENTS) + 1:]
    return path


def is_python_file(path):
    _, ext = os.path.splitext(path)
    return ext.lower() == '.py'
