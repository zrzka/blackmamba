#!python3

import blackmamba.toggle_comments
import blackmamba.ide
import blackmamba.file_picker
import blackmamba.dash
import blackmamba.action_picker
import blackmamba.analyzer
import blackmamba.experimental.tester
import blackmamba.updates
import blackmamba.outline
from blackmamba.key_commands import register_key_command
from blackmamba.uikit import UIKeyModifierCommand, UIKeyModifierShift, UIKeyModifierControl
from blackmamba.log import warn, info, error
import blackmamba.system as system

__version__ = '0.0.18'
_LATEST_VERSION_COMPATIBILITY_TEST = (311008, '3.1.1')


def _make_select_tab(index):
    def select_tab():
        blackmamba.ide.select_tab(index)
    return select_tab


def _register_default_key_commands():
    info('Registering default key commands...')

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
         blackmamba.ide.select_previous_tab),
        ('L', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.outline.outline_quickly,
         'Outline Quickly...')
    ]

    for command in commands:
        register_key_command(*command)

    for i in range(9):
        register_key_command(str(i + 1), UIKeyModifierCommand, _make_select_tab(i))

    info('Default key commands registered')


def _is_compatible_with_pythonista():
    info('Pythonista {} ({})'.format(system.PYTHONISTA_VERSION, system.PYTHONISTA_BUNDLE_VERSION))

    local_release = blackmamba.updates.get_local_release()
    if local_release:
        info('Black Mamba {} (tag {})'.format(__version__, local_release['tag_name']))
    else:
        info('Black Mamba {} (tag unknown, not installed via installation script)'.format(__version__))

    return system.PYTHONISTA_BUNDLE_VERSION <= _LATEST_VERSION_COMPATIBILITY_TEST[0]


def main(**kwargs):
    info('Black Mamba initialization...')

    if not system.PYTHONISTA:
        error('Skipping, not running under Pythonista')
        return

    compatible = _is_compatible_with_pythonista()

    if 'allow_incompatible_pythonista_version' in kwargs:
        warn('allow_incompatible_pythonista_version argument removed, has no effect')

    blackmamba.updates.check()
    _register_default_key_commands()

    info('Black Mamba initialized')

    if not compatible:
        error('Installed Black Mamba version is not tested with current version of Pythonista')
        error('Latest compatibility tests were made with Pythonista {} ({})'.format(
            _LATEST_VERSION_COMPATIBILITY_TEST[1],
            _LATEST_VERSION_COMPATIBILITY_TEST[0]))
        error('Update Black Mamba or use at your own risk')

    return compatible


if __name__ == '__main__':
    main()
