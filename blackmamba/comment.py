#!python3

import re
import sys


def _comment_line(line, hash_col_index=0):
    if not line.find('#') == -1:
        return line

    if not line.strip():
        return line

    return line[:hash_col_index] + '# ' + line[hash_col_index:]


_UNCOMMENT_RE = re.compile('\A(\s*)#( ?)(.*)\Z', re.DOTALL)


def _uncomment_line(line):
    if line.find('#') == -1:
        return line

    match = _UNCOMMENT_RE.search(line)
    if match:
        result = match.group(1) + match.group(3)
    else:
        result = line
    return result


_HASH_INDEX_RE = re.compile('\A(\s*)')


def _hash_col_index(lines):
    index = sys.maxsize

    for line in lines:
        if not line.strip():
            continue

        match = _HASH_INDEX_RE.search(line)

        if not match:
            continue

        if len(match.group(1)) < index:
            index = len(match.group(1))

    if index == sys.maxsize:
        index = 0

    return index


def _toggle_lines(lines):
    if not lines:
        return lines

    if lines[0].strip().startswith('#'):
        comment = False
        hash_col_index = None
    else:
        comment = True
        hash_col_index = _hash_col_index(lines)

    replacement = []

    for line in lines:
        if comment:
            replacement.append(_comment_line(line, hash_col_index))
        else:
            replacement.append(_uncomment_line(line))

    return replacement


def toggle_comments():
    import editor

    selection_range = editor.get_selection()

    if not selection_range:
        # No file opened in the editor
        return

    text = editor.get_text()

    selected_lines_range = editor.get_line_selection()
    selected_lines_text = text[selected_lines_range[0]:selected_lines_range[1]]
    selected_lines = selected_lines_text.splitlines(True)

    last_line_deleted = False
    if len(selected_lines) > 1:
        # Ignore the last line selection if there's just cursor at the beginning of
        # this line and nothing is selected
        last_line = selected_lines[-1]

        if selected_lines_range[1] - len(last_line) == selection_range[1]:
            last_line_deleted = True
            del selected_lines[-1]
            selected_lines_range = (selected_lines_range[0], selected_lines_range[1] - len(last_line) - 1)

    replacement = ''.join(_toggle_lines(selected_lines))

    if last_line_deleted:
        replacement = replacement[:-1]

    editor.replace_text(selected_lines_range[0], selected_lines_range[1], replacement)
    editor.set_selection(selected_lines_range[0], selected_lines_range[0] + len(replacement))
