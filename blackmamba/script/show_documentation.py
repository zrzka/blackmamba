#!python3
"""
Script name ``show_documentation.py``.

Shows documentation for the symbol around cursor. If definition can't be found,
HUD informs you. If there're more than one definitions, dialog appears where
you can select which one to show.

Documentation is displayed as an overlay, which can be closed by the
``Ctrl-W`` shortcut or by tapping on the ``X`` button.

JEDI must be enabled, see :ref:`configuration`.
"""

from blackmamba.uikit.picker import PickerView, PickerItem, PickerDataSource
import editor
import console
import blackmamba.ide.tab as tab
import blackmamba.ide.source as source
import os
import jedi
from blackmamba.config import get_config_value
import blackmamba.log as log
import ui
import blackmamba.uikit.overlay as overlay
from blackmamba.ide.theme import get_theme_value, get_editor_font


class LocationPickerItem(PickerItem):
    def __init__(self, path, line, display_folder, definition):
        super().__init__(
            '{}, line {}'.format(os.path.basename(path), line),
            display_folder
        )
        self.path = path
        self.line = line
        self.definition = definition

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
    def __init__(self, definitions):
        super().__init__()

        items = [
            LocationPickerItem(
                definition.module_name,
                definition.line,
                definition.full_name,
                definition
            )
            for definition in definitions
        ]

        self.items = items


def _show_documentation(definition):
    reuse = get_config_value('documentation.reuse', True)
    frame = get_config_value('documentation.frame', (630, 110, 730, 350))
    tag = '__blackmamba.show_documentation'
    if not reuse:
        tag += ':{}'.format(definition.full_name)

    manager = overlay.get_manager()

    o = manager.get_overlay(tag)
    if o:
        o.title = definition.name
        o.content_view.text = definition.docstring()
        o.expand()
        o.become_active()
        return

    tv = ui.TextView(
        text=definition.docstring(),
        background_color=get_theme_value('background_color'),
        text_color=get_theme_value('text_color'),
        font=get_editor_font()
    )
    tv.editable = False

    window_size = ui.get_window_size()
    x = frame[0]
    y = frame[1]
    width = min(window_size[0] - x - 12, frame[2])
    height = min(window_size[1] - y - 12, frame[3])
    manager.present(definition.name, tv, frame=(x, y, width, height), tag=tag)


def _select_location(definitions):
    def action(item, shift_enter):
        _show_documentation(item.definition)

    v = PickerView()
    v.name = '{} definitions'.format(definitions[0].name)
    v.datasource = LocationDataSource(definitions)

    v.shift_enter_enabled = False
    v.help_label.text = (
        '⇅ - select • Enter - show documentation'
        '\n'
        'Esc - close • Cmd . - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter location...'
    v.did_select_item_action = action
    v.present('sheet')
    v.wait_modal()


def main():
    if not get_config_value('general.jedi', False):
        log.warn('show_documentation disabled, you can enable it by setting general.jedi to True')
        return

    path = editor.get_path()
    if path is None:
        return

    if not path.endswith('.py'):
        return

    tab.save()

    text = editor.get_text()
    if not text:
        return

    line = source.get_line_number()
    column = source.get_column_index()

    if line is None or column is None:
        return

    script = jedi.api.Script(text, line, column, path)
    definitions = [
        d for d in script.goto_definitions()
        if d.module_path and d.line
    ]

    if not definitions:
        console.hud_alert('Documentation not found', 'error')
        return

    if len(definitions) == 1:
        _show_documentation(definitions[0])
    else:
        _select_location(definitions)


if __name__ == '__main__':
    main()
