#!python3

from blackmamba.project.project import Project
import editor
import re


ALLOWED_CHAR = re.compile('[a-zA-Z0-9_]')


def _allowed_char(ch):
    return ALLOWED_CHAR.match(ch) is not None


def _query():
    text = editor.get_text()

    if not text:
        return None

    selection = editor.get_selection()

    # Begin/end differs, query for selection
    if not selection[0] == selection[1]:
        return text[selection[0]:selection[1]]

    # Try to select current keyword around current cursor position
    bi = selection[0]
    while bi > 0 and _allowed_char(text[bi - 1:bi]):
        bi -= 1

    ei = selection[1]
    while ei < len(text) and _allowed_char(text[ei:ei + 1]):
        ei += 1

    return text[bi:ei]


def jump_to_definition():
    path = editor.get_path()
    if not path:
        return

    symbol = _query()

    if not symbol:
        return

    p = Project.by_path(path)
    if not p:
        return

    print(p.find_symbol_definition(symbol))