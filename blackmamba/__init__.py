#!python3

"""Black Mamba initialization module.

The only requirement is to call `blackmamba.main`. Example::

    import blackmamba
    blackmamba.main()

.. warning:: Do not add top level imports which depends on Pythonista modules. Module
    must be importable on any other platform. Add these imports to specific functions
    decorated with `blackmamba.system.Pythonista` and / or
    `blackmamba.system.iOS`.
"""

from blackmamba.log import info, error, get_level, set_level, ERROR
import blackmamba.system as system

__version__ = '1.5.0'
__author__ = 'Robert Vojta'

_LATEST_VERSION_COMPATIBILITY_TEST = (320000, '3.2')


def _register_key_command(input, modifier, function, title=None):
    from blackmamba.uikit.keyboard import register_key_command
    import blackmamba.ide.script as script
    import os

    def make_run_script(path):
        path = os.path.join(
            os.path.expanduser('site-packages-3/blackmamba/script'),
            path
        )

        def run():
            script.run_script(path)

        return run

    if isinstance(function, str):
        function = make_run_script(function)

    register_key_command(input, modifier, function, title)


@system.Pythonista(appex=False)
@system.iOS('11.0')
def _register_ios11_default_key_commands():
    from blackmamba.uikit.keyboard import UIKeyModifier

    commands = [
        ('E', UIKeyModifier.COMMAND,
         'drag_and_drop.py', 'Drag & Drop')
    ]

    for command in commands:
        _register_key_command(*command)


@system.Pythonista(appex=False)
def _register_default_key_commands():
    from blackmamba.uikit.keyboard import UIKeyModifier, UIKeyInput
    import blackmamba.ide.tab as tab
    import blackmamba.ide.source as source
    import blackmamba.uikit.overlay as overlay

    info('Registering default key commands...')

    commands = [
        # Scripts allowed to be used in the wrench
        ('/', UIKeyModifier.COMMAND,
         'toggle_comments.py', 'Toggle comments'),
        ('N', UIKeyModifier.COMMAND,
         'new_file.py', 'New file'),
        ('W', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT,
         'close_all_tabs_except_current_one.py', 'Close tabs except current one'),
        ('O', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT,
         'open_quickly.py', 'Open quickly...'),
        ('0', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT,
         'search_dash.py', 'Search in Dash'),
        ('R', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT,
         'run_quickly.py', 'Run quickly...'),
        ('A', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT,
         'action_quickly.py', 'Action quickly...'),
        ('B', UIKeyModifier.control | UIKeyModifier.SHIFT,
         'analyze.py', 'Analyze & Check style'),
        ('K', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT,
         'clear_annotations.py', 'Clear annotations'),
        ('U', UIKeyModifier.COMMAND,
         'run_unit_tests.py', 'Run unit tests...'),
        ('L', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT,
         'outline_quickly.py', 'Outline quickly...'),
        ('L', UIKeyModifier.CONTROL,
         'jump_to_line.py', 'Jump to line...'),
        ('J', UIKeyModifier.COMMAND | UIKeyModifier.CONTROL,
         'jump_to_definition.py', 'Jump to definition...'),
        ('U', UIKeyModifier.COMMAND | UIKeyModifier.CONTROL,
         'find_usages.py', 'Find usages...'),
        ('?', UIKeyModifier.COMMAND | UIKeyModifier.CONTROL,
         'show_documentation.py', 'Show documentation'),
        ('R', UIKeyModifier.COMMAND | UIKeyModifier.ALTERNATE,
         'refactoring/rename.py', 'Refactor - Rename'),
        ('O', UIKeyModifier.COMMAND | UIKeyModifier.ALTERNATE,
         'refactoring/organize_imports.py', 'Refactor - Organize imports'),
        ('E', UIKeyModifier.COMMAND | UIKeyModifier.ALTERNATE,
         'refactoring/expand_star_imports.py', 'Refactor - Expand star imports'),
        ('F', UIKeyModifier.COMMAND | UIKeyModifier.ALTERNATE,
         'refactoring/futurize.py', 'Refactor - Futurize'),

        # Still keyboard only
        ('0', UIKeyModifier.COMMAND,
         tab.toggle_navigator,
         'Toggle navigator'),
        (UIKeyInput.UP_ARROW, UIKeyModifier.CONTROL,
         source.page_up),
        (UIKeyInput.DOWN_ARROW, UIKeyModifier.CONTROL,
         source.page_down),
        ('W', UIKeyModifier.CONTROL,
         overlay.dismiss_active_overlay)
    ]

    for command in commands:
        _register_key_command(*command)

    def _make_select_tab(index):
        def select_tab():
            tab.select_tab(index)
        return select_tab

    for i in range(9):
        _register_key_command(str(i + 1), UIKeyModifier.COMMAND, _make_select_tab(i))

    # No need to show Cmd-[Shift]-S to users
    _log_level = get_level()
    set_level(ERROR)

    def save_all():
        tab.save(True)

    _register_key_command('S', UIKeyModifier.COMMAND, tab.save)
    _register_key_command('S', UIKeyModifier.COMMAND | UIKeyModifier.SHIFT, save_all)
    set_level(_log_level)

    info('Default key commands registered')


@system.Pythonista(appex=False)
def _check_compatibility():
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


@system.Pythonista(appex=False)
def _check_for_updates():
    import blackmamba.update
    blackmamba.update.check()


@system.Pythonista()
@system.catch_exceptions
def _main(config=None):
    # It's here because Sphinx doesn't show documentation for decorated
    # functions
    from blackmamba.config import update_config_with_dict, get_config_value
    info('Black Mamba initialization...')
    if config:
        update_config_with_dict(config)
    _check_compatibility()
    if get_config_value('general.register_key_commands', True):
        _register_default_key_commands()
        _register_ios11_default_key_commands()
    info('Black Mamba initialized')
    _check_for_updates()


def main(config=None):
    """Black Mamba initialization.

    Call this function from `pythonista_startup.py` (`site-packages-3`) file.

    Args:
        config (optional): Dictionary with configuration

    Example::

        import blackmamba

        config = {
            'general': {
                'jedi': True
            }
        }

        blackmamba.main(config)

    See `pythonista_startup.py <https://github.com/zrzka/blackmamba/blob/master/pythonista_startup.py>`_
    for more examples.
    """
    _main(config)


if __name__ == '__main__':
    main()
