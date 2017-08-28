#!python3

import blackmamba.toggle_comments
import blackmamba.ide
import blackmamba.file_picker
import blackmamba.dash
import blackmamba.action_picker
import blackmamba.analyzer
import blackmamba.experimental.tester
import blackmamba.updates
from blackmamba.key_commands import register_key_command
from blackmamba.uikit import UIKeyModifierCommand, UIKeyModifierShift, UIKeyModifierControl
import plistlib
import os
import sys

__version__ = '0.0.15'
_LATEST_VERSION_COMPATIBILITY_TEST = (301016, '3.1')


def _make_select_tab(index):
    def select_tab():
        blackmamba.ide.select_tab(index)
    return select_tab


def _register_default_key_commands():
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
         blackmamba.file_picker.script_quickly,
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


def _is_compatible_with_pythonista():
    plist_path = os.path.abspath(os.path.join(sys.executable,
                                 '..', 'Info.plist'))
    plist = plistlib.readPlist(plist_path)

    version_string = plist['CFBundleShortVersionString']
    bundle_version = int(plist['CFBundleVersion'])

    print('Pythonista {} ({})'.format(version_string, bundle_version))

    local_release = blackmamba.updates.get_local_release()
    if local_release:
        print('Black Mamba {} (tag {})'.format(__version__, local_release['tag_name']))
    else:
        print('Black Mamba {} (tag unknown, not installed via installation script)'.format(__version__))

    if bundle_version > _LATEST_VERSION_COMPATIBILITY_TEST[0]:
        sys.stderr.write('Not tested combination, please, update Black Mamba\n')
        sys.stderr.write('Latest tests were made with Pythonista {} ({})\n'.format(
            _LATEST_VERSION_COMPATIBILITY_TEST[1],
            _LATEST_VERSION_COMPATIBILITY_TEST[0]))
        return False

    return True


def main(allow_incompatible_pythonista_version=False):
    print('Black Mamba initialization...')
    compatible = _is_compatible_with_pythonista()

    if compatible or allow_incompatible_pythonista_version:
        blackmamba.updates.check()
        _register_default_key_commands()

    print('Black Mamba initialized')


if __name__ == '__main__':
    main(True)
