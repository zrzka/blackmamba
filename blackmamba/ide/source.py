#!python3

import editor
from blackmamba.config import get_config_value


def get_line_count():
    text = editor.get_text()

    if text is None:
        return None

    return len(text.splitlines())


def get_line_number():
    text = editor.get_text()

    if text is None:
        return None

    return text.count('\n', 0, editor.get_selection()[0]) + 1


def get_column_index():
    text = editor.get_text()

    if text is None:
        return None

    col = 0
    index = editor.get_selection()[0]
    while index > 0:
        if text[index - 1] == '\n':
            break
        index -= 1
        col += 1

    return col


def scroll_to_line(line_number, relative=False):
    text = editor.get_text()
    if not text:
        return

    if relative:
        current_line = get_line_number()
        line_count = get_line_count()

        if current_line is None or line_count is None:
            return

        line_number = max(min(current_line + line_number, line_count), 1)

    # https://github.com/omz/Pythonista-Issues/issues/365
    start = 0
    for index, line in enumerate(text.splitlines(True)):
        if index == line_number - 1:
            editor.set_selection(start)
            return
        start += len(line)
    editor.set_selection(start)


def page_up():
    scroll_to_line(-get_config_value('general.page_line_count', 40), True)


def page_down():
    scroll_to_line(get_config_value('general.page_line_count', 40), True)
