#!python3

from blackmamba.log import info, error, get_level, set_level, ERROR
import blackmamba.system as system

__version__ = '0.0.23'
__author__ = 'Robert Vojta'

_LATEST_VERSION_COMPATIBILITY_TEST = (311009, '3.1.1')


@system.Pythonista()
@system.iOS('11.0')
def _register_ios11_default_key_commands():
    from blackmamba.drag_provider import drag_provider_dialog
    from blackmamba.key_command import register_key_command, UIKeyModifierCommand

    commands = [
        ('E', UIKeyModifierCommand,
         drag_provider_dialog,
         'Drag Provider')
    ]

    for command in commands:
        register_key_command(*command)


@system.Pythonista()
def _register_default_key_commands():
    import blackmamba.comment
    import blackmamba.ide
    import blackmamba.file_picker
    import blackmamba.dash
    import blackmamba.action_picker
    import blackmamba.analyzer
    import blackmamba.experimental.tester
    import blackmamba.outline
    import blackmamba.project.jump_to_definition
    from blackmamba.key_command import (
        register_key_command, UIKeyModifierCommand, UIKeyModifierShift, UIKeyModifierControl
    )

    info('Registering default key commands...')

    commands = [
        ('/', UIKeyModifierCommand,
         blackmamba.comment.toggle_comments,
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
         'Outline Quickly...'),
        ('L', UIKeyModifierControl,
         blackmamba.ide.jump_to_line_dialog,
         'Jump to line...'),
        ('D', UIKeyModifierCommand | UIKeyModifierShift,
         blackmamba.project.jump_to_definition.jump_to_definition,
         'Jump to definition...')
    ]

    for command in commands:
        register_key_command(*command)

    def _make_select_tab(index):
        def select_tab():
            blackmamba.ide.select_tab(index)
        return select_tab

    for i in range(9):
        register_key_command(str(i + 1), UIKeyModifierCommand, _make_select_tab(i))

    _register_ios11_default_key_commands()

    # No need to log Cmd-S (Save) to users
    _log_level = get_level()
    set_level(ERROR)
    register_key_command('S', UIKeyModifierCommand, blackmamba.ide.save)
    set_level(_log_level)

    info('Default key commands registered')


@system.Pythonista()
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
    info('Black Mamba initialized')


if __name__ == '__main__':
    main()
