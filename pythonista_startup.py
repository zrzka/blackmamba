#!python3

import blackmamba
import blackmamba.log as log

# Default value is INFO. Use ERROR if you'd like to make Black
# Mamba quiet. Only errors will be printed.
log.set_level(log.INFO)

# Check blackmamba.config._DEFAULTS for default values
config = {
    'update': {
        'enabled': True,
        'interval': 3600
    },
    'file_picker': {
        'ignore_folders': {
            '': ['.git'],
            '.': ['Pythonista', '.Trash', 'Examples',
                  'site-packages-2', 'site-packages', 'stash_extensions'],
            'site-packages-3': ['blackmamba'],
            'Development': ['bm-pip-backup']
        }
    },
    'analyzer': {
        'hud_alert_delay': 1.0,
        'ignore_codes': None,
        'max_line_length': 127,
        'remove_whitespaces': True
    },
    'tester': {
        'hud_alert_delay': 1.0,
        'hide_console': True
    }
}


def register_custom_shortcuts():
    import blackmamba.ide as ide
    import blackmamba.key_command as kc

    # Launch `StaSh` (= custom action title) via Cmd-Shift-S
    if ide.action_exists('StaSh'):
        def launch_stash():
            ide.run_action('StaSh')

        kc.register_key_command(
            'S',  # Shortcut key
            kc.UIKeyModifierCommand | kc.UIKeyModifierShift,  # Shortcut modifier keys
            launch_stash,  # Function to call
            'Launch StaSh')  # Optional discoverability title (hold down Cmd)

# Or you can use run_script instead of action to launch StaSh
# if ide.script_exists('launch_stash.py'):
#     def launch_stash():
#         ide.run_script('launch_stash.py')
#
#     kc.register_key_command(
#         'S',
#         kc.UIKeyModifierCommand | kc.UIKeyModifierShift,
#         launch_stash,
#         'Launch StaSh')


def main():
    # The only requirement is to call main(). You can omit `config=config`
    # if you'd like to use default config.
    blackmamba.main(config=config)
    register_custom_shortcuts()


if __name__ == 'pythonista_startup':
    main()
