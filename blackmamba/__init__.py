#!python3

import blackmamba.toggle_comments
import blackmamba.ide
import blackmamba.file_picker
import blackmamba.dash
import blackmamba.script_picker
import blackmamba.action_picker
import blackmamba.analyzer
import blackmamba.experimental.tester
from blackmamba.key_commands import register_key_command
from blackmamba.uikit import UIKeyModifierCommand, UIKeyModifierShift, UIKeyModifierControl


def _make_select_tab(index):
    def select_tab():
        blackmamba.ide.select_tab(index)
    return select_tab


def register_default_key_commands():
    print('Registering default key commands...')

    commands = [
        ('/', UIKeyModifierCommand,
         blackmamba.toggle_comments.toggle_comments,
         'Toggle Comments'),
        ('N', UIKeyModifierCommand,
         blackmamba.ide.new_file,
         'New File'),
        ('T', UIKeyModifierCommand,
         blackmamba.ide.new_tab,
         'New Tab'),
        ('0', UIKeyModifierCommand,
         blackmamba.ide.toggle_navigator,
         'Toggle Navigator'),
        ('W', UIKeyModifierCommand,
         blackmamba.ide.close_current_tab,
         'Close Tab'),
        ('W', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.ide.close_all_tabs_except_current_one,
         'Close Tabs Except Current One'),
        ('O', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.file_picker.open_quickly,
         'Open Quickly...'),
        ('0', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.dash.search_dash,
         'Search in Dash'),
        ('R', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.script_picker.script_quickly,
         'Run Quickly...'),
        ('A', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.action_picker.action_quickly,
         'Action Quickly...'),
        ('B', UIKeyModifierControl | UIKeyModifierShift,
         blackmamba.analyzer.analyze,
         'Analyze & Check Style'),
        ('K', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.analyzer.clear_annotations,
         'Clear Annotations'),
        ('U', UIKeyModifierCommand,
         blackmamba.experimental.tester.run_script_unit_tests,
         'Run Unit Tests...'),
        ('\t', UIKeyModifierControl,
         blackmamba.ide.select_next_tab,
         'Show Next Tab'),
        ('\t', UIKeyModifierControl | UIKeyModifierShift,
         blackmamba.ide.select_previous_tab,
         'Show Previous Tab'),
        (']', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.ide.select_next_tab),
        ('[', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.ide.select_previous_tab)
    ]

    for command in commands:
        register_key_command(*command)

    for i in range(9):
        register_key_command(str(i + 1), UIKeyModifierCommand, _make_select_tab(i))

    print('Default key commands registered')


if __name__ == '__main__':
    register_default_key_commands()
