#!python3

from blackmamba.project.project import Project
from blackmamba.picker import load_picker_view, PickerItem, PickerDataSource
import blackmamba.log as log
import editor
import re
import console
import blackmamba.ide as ide
import os
import ui

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


def _open_and_scroll(path, line):
    if editor.get_path() == path:
        ide.scroll_to_line(line)
    else:
        def scroll():
            ide.scroll_to_line(line)
        editor.open_file(path, new_tab=True)
        ui.delay(scroll, 0.2)


class LocationPickerItem(PickerItem):
    def __init__(self, path, line, display_folder):
        super().__init__(
            '{}, line {}'.format(os.path.basename(path), line),
            display_folder
        )
        self.path = path
        self.line = line

    def matches_title(self, terms):
        if not terms:
            return True

        start = 0
        for t in terms:
            start = self.path.find(t, start)

            if start == -1:
                return False

            start += len(t)

        return True


class LocationDataSource(PickerDataSource):
    def __init__(self, symbol, locations):
        super().__init__()

        home_folder = os.path.expanduser('~/Documents')

        items = [
            LocationPickerItem(
                location[0],
                location[1],
                ' • '.join(os.path.dirname(location[0])[len(home_folder) + 1:].split(os.sep))
            )
            for location in locations
        ]

        self.items = items


def _select_location(symbol, locations):
    def open_location(item, shift_enter):
        _open_and_scroll(item.path, item.line)

    v = load_picker_view()
    v.name = '{} locations'.format(symbol)
    v.datasource = LocationDataSource(symbol, locations)

    v.shift_enter_enabled = False
    v.help_label.text = (
        '⇅ - select • Enter - open file and scroll to location'
        '\n'
        'Esc - close • Ctrl [ - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter files...'
    v.did_select_item_action = open_location
    v.present('sheet')
    v.wait_modal()


def jump_to_definition():
    path = editor.get_path()
    if not path:
        console.hud_alert('Open some file', 'error')
        return

    symbol = _query()
    log.debug('Jump to definition symbol "{}"'.format(symbol))

    if not symbol:
        console.hud_alert('Select symbol or place cursor in it', 'error')
        return

    p = Project.by_path(path)
    if not p:
        console.hud_alert('File not in a project', 'error')
        return

    locations = p.find_symbol_definition(symbol)
    if not locations:
        console.hud_alert('Symbol not found', 'error')
        return

    if len(locations) == 1:
        path, line = locations[0]
        _open_and_scroll(path, line)
    else:
        _select_location(symbol, locations)


if __name__ == '__main__':
    jump_to_definition()
