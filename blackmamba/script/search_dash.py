#!python3
"""
Script name ``search_dash.py``.

Opens `Dash <https://kapeli.com/dash_ios>`_ application with selected text or a symbol around cursor position.
"""

import editor
import urllib.parse
import webbrowser
import re

_ALLOWED_CHAR = re.compile('[a-zA-Z0-9_]')


def _encode_query(query):
    return urllib.parse.quote_plus(query, safe='', encoding=None, errors=None)


def _dash_url(query):
    return 'dash://' + _encode_query(query)


def _allowed_char(ch):
    return _ALLOWED_CHAR.match(ch) is not None


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


def main(query=None):
    """Opens Dash documentation browser.

    If you do not provide query, current selection will be used. If there's
    nothing selected in the editor, cursor position is used to find identifier.

    Nothing happens if query is not provided and identifier can't be found.

    Args:
        query: Text to search in Dash
    """

    q = query or _query()

    if not q:
        return

    webbrowser.open(_dash_url(q))


if __name__ == '__main__':
    main()
