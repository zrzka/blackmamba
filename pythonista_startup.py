#!python3

#
# Must be added to:
#
#   ~/Documents/site-packages-3
#

# Check blackmamba.config._DEFAULTS for default values
config = {
    'general': {
        'jedi': True
        # Uncomment to disable keyboard shortcuts
        # 'register_key_commands': False
    },
    'update': {
        'enabled': True,
        'interval': 3600
    },
    'file_picker': {
        'ignore_folders': {
            '': ['.git'],
            '.': ['Pythonista', '.Trash', 'Examples',
                  'site-packages-2', 'site-packages', 'stash_extensions'],
            'site-packages-3': ['blackmamba', 'bm-pip-backup'],
            'Working Copy': ['bm-pip-backup']
        }
    },
    'analyzer': {
        'hud_alert_delay': 1.0,
        'ignore_codes': ['E114', 'E116'],
        'max_line_length': 127,
        'remove_whitespaces': True
    },
    'tester': {
        'hud_alert_delay': 1.0,
        'hide_console': True
    },
    'drag_and_drop': {
        'ignore_folders': {
            '': ['.git'],
            '.': ['Pythonista', '.Trash', 'Examples',
                  'site-packages-2', 'site-packages', 'stash_extensions'],
            'Working Copy': ['bm-pip-backup']
        }
    }
}


def register_custom_shortcuts():
    import blackmamba.ide.action as action
    from blackmamba.uikit.keyboard import register_key_command, UIKeyModifier

    # Launch `StaSh` (= custom action title) via Ctrl-S
    action = action.get_action('StaSh')
    if action:
        def launch_stash():
            action.run()

        register_key_command(
            'S',
            UIKeyModifier.control,
            launch_stash,
            'Launch StaSh'
        )


def main():
    import blackmamba
    import blackmamba.log as log

    # Default value is INFO. Use ERROR if you'd like to make Black
    # Mamba quiet. Only errors will be printed.
    log.set_level(log.INFO)

    # The only requirement is to call main(). You can omit `config=config`
    # if you'd like to use default config.
    blackmamba.main(config=config)
    register_custom_shortcuts()

    # If you'd like to hide console after Black Mamba starts, just uncomment
    # following lines
    # import console
    # console.hide_output()


if __name__ == 'pythonista_startup':
    import traceback
    try:
        main()
    except Exception:
        print(traceback.format_exc())
        print('Failed to process pythonista_startup.py')
