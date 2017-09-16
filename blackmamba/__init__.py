#!python3

from blackmamba.log import info, error, get_level, set_level, ERROR
import blackmamba.system as system

__version__ = '0.0.25'
__author__ = 'Robert Vojta'

_LATEST_VERSION_COMPATIBILITY_TEST = (311009, '3.1.1')


def _register_key_command(input, modifier_flags, function, title=None):
    from blackmamba.key_command import register_key_command
    import blackmamba.ide
    import os

    def make_run_script(script):
        path = os.path.join(
            os.path.expanduser('site-packages-3/blackmamba/script'),
            script
        )

        def run():
            blackmamba.ide.run_script(path)

        return run

    if isinstance(function, str):
        function = make_run_script(function)

    register_key_command(input, modifier_flags, function, title)


@system.Pythonista(appex=False)
@system.iOS('11.0')
def _register_ios11_default_key_commands():
    from blackmamba.key_command import UIKeyModifierCommand

    commands = [
        ('E', UIKeyModifierCommand,
         'drag_provider.py', 'Drag Provider')
    ]

    for command in commands:
        _register_key_command(*command)


@system.Pythonista(appex=False)
def _register_default_key_commands():
    import blackmamba.ide
    from blackmamba.key_command import (
        UIKeyModifierCommand, UIKeyModifierShift, UIKeyModifierControl,
        UIKeyInputUpArrow, UIKeyInputDownArrow
    )

    info('Registering default key commands...')

    commands = [
        # Scripts allowed to be used in the wrench
        ('/', UIKeyModifierCommand,
         'toggle_comments.py', 'Toggle Comments'),
        ('N', UIKeyModifierCommand,
         'new_file.py', 'New File'),
        ('T', UIKeyModifierCommand,
         'new_tab.py', 'New Tab'),
        ('W', UIKeyModifierCommand | UIKeyModifierShift,
         'close_all_tabs_except_current_one.py', 'Close Tabs Except Current One'),
        ('O', UIKeyModifierCommand | UIKeyModifierShift,
         'open_quickly.py', 'Open Quickly...'),
        ('0', UIKeyModifierCommand | UIKeyModifierShift,
         'search_dash.py', 'Search in Dash'),
        ('R', UIKeyModifierCommand | UIKeyModifierShift,
         'run_quickly.py', 'Run Quickly...'),
        ('A', UIKeyModifierCommand | UIKeyModifierShift,
         'action_quickly.py', 'Action Quickly...'),
        ('B', UIKeyModifierControl | UIKeyModifierShift,
         'analyze.py', 'Analyze & Check Style'),
        ('K', UIKeyModifierCommand | UIKeyModifierShift,
         'clear_annotations.py', 'Clear Annotations'),
        ('U', UIKeyModifierCommand,
         'run_unit_tests.py', 'Run Unit Tests...'),
        ('L', UIKeyModifierCommand | UIKeyModifierShift,
         'outline_quickly.py', 'Outline Quickly...'),
        ('L', UIKeyModifierControl,
         'jump_to_line.py', 'Jump to line...'),
        ('D', UIKeyModifierCommand | UIKeyModifierShift,
         'jump_to_definition.py', 'Jump to definition...'),

        # Still keyboard only
        ('0', UIKeyModifierCommand,
         blackmamba.ide.toggle_navigator,
         'Toggle Navigator'),
        ('W', UIKeyModifierCommand,
         blackmamba.ide.close_current_tab,
         'Close Tab'),
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
        (UIKeyInputUpArrow, UIKeyModifierControl,
         blackmamba.ide.page_up),
        (UIKeyInputDownArrow, UIKeyModifierControl,
         blackmamba.ide.page_down)
    ]

    for command in commands:
        _register_key_command(*command)

    def _make_select_tab(index):
        def select_tab():
            blackmamba.ide.select_tab(index)
        return select_tab

    for i in range(9):
        _register_key_command(str(i + 1), UIKeyModifierCommand, _make_select_tab(i))

    # No need to log Cmd-S (Save) to users
    _log_level = get_level()
    set_level(ERROR)
    _register_key_command('S', UIKeyModifierCommand, blackmamba.ide.save)
    set_level(_log_level)

    info('Default key commands registered')


@system.Pythonista(appex=False)
def _check_compatibility_and_updates():
    import blackmamba.update
    info('Pythonista {} ({})'.format(system.PYTHONISTA_VERSION, system.PYTHONISTA_BUNDLE_VERSION))

    local_release = blackmamba.update.get_local_release()
    if local_release:
        info('Black Mamba {} (tag {})'.format(__version__, local_release['tag_name']))
    else:
        info('Black Mamba {} (tag unknown, not installed via installation script)'.format(__version__))

    if system.PYTHONISTA_BUNDLE_VERSION > _LATEST_VERSION_COMPATIBILITY_TEST[0]:
        error('Installed Black Mamba version is not tested with current version of Pythonista')
        error('Latest compatibility tests were made with Pythonista {} ({})'.format(
            _LATEST_VERSION_COMPATIBILITY_TEST[1],
            _LATEST_VERSION_COMPATIBILITY_TEST[0]))
        error('Update Black Mamba or use at your own risk')

    blackmamba.update.check()


@system.Pythonista()
@system.catch_exceptions
def main(config=None):
    from blackmamba.config import update_config_with_dict, get_config_value
    info('Black Mamba initialization...')
    if config:
        update_config_with_dict(config)
    _check_compatibility_and_updates()
    if get_config_value('general.register_key_commands', True):
        _register_default_key_commands()
        _register_ios11_default_key_commands()
    info('Black Mamba initialized')


if __name__ == '__main__':
    main()
