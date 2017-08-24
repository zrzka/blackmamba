#!python3

import blackmamba.toggle_comments
import blackmamba.ide
import blackmamba.file_picker
import blackmamba.dash
import blackmamba.script_picker
import blackmamba.action_picker
import blackmamba.analyzer
from blackmamba.key_commands import register_key_command
from blackmamba.uikit import UIKeyModifierCommand, UIKeyModifierShift, UIKeyModifierControl


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
         'Clear Annotations')
    ]

    for command in commands:
        register_key_command(*command)

    print('Default key commands registered')


if __name__ == '__main__':
    register_default_key_commands()
