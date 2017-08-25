#!python3

import editor


def _comment_line(line):
    return '# ' + line


def _uncomment_line(line):
    if not line.strip().startswith('#'):
        return line

    start = line.find('# ')
    if start == -1:
        start = line.find('#') + 1
    else:
        start += 2

    return line[start:]


def toggle_comments():
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

    if selected_lines_text.strip().startswith('#'):
        toggle_comment = _uncomment_line
    else:
        toggle_comment = _comment_line

    replacement = ''

    for line in selected_lines:
        replacement += toggle_comment(line)

    if last_line_deleted:
        replacement = replacement[:-1]

    editor.replace_text(selected_lines_range[0], selected_lines_range[1], replacement)
    editor.set_selection(selected_lines_range[0], selected_lines_range[0] + len(replacement))
