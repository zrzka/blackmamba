#!python3

import blackmamba as bm

# Default: True
bm.updates.check_for_updates = True

# Default: 86400 seconds (1 day)
bm.updates.check_interval = 3600

# ''           : any parent folder
# '.'          : ~/Documents parent folder
# 'Development': ~/Documents/Development parent folder
#
# Used for both Run Quickly & Open Quickly

# Default:
#
# {
#     '': ['.git'],
#     '.': ['.Trash', 'Examples',
#           'site-packages', 'site-packages-2', 'site-packages-3']
# }
bm.file_picker.ignore_folders = {
    '': ['.git'],
    '.': ['Pythonista', '.Trash', 'Examples',
          'site-packages-2', 'site-packages', 'stash_extensions'],
    'site-packages-3': ['blackmamba'],
    'Development': ['bm-pip-backup']
}

# Default: 1.0
bm.analyzer.hud_alert_delay = 1.0

# Default: ['W391', 'W293']
bm.analyzer.ignore_codes = None

# Default: 79
bm.analyzer.max_line_length = 127

# Default: True
bm.analyzer.remove_whitespaces = True

# Default: 1.0
bm.experimental.tester.hud_alert_delay = 1.0

# Default: True
bm.experimental.tester.hide_console = True

# Default: INFO
bm.log.level = bm.log.NOTSET

bm.main()  # <---- THIS MUST BE CALLED IN ORDER TO PROPERLY INITIALIZE BLACK MAMBA

################################################################
# Custom keyboard shortcuts                                    #
################################################################

# Launch StaSh (= custom action title) via Cmd-Shift-S
if bm.ide.action_exists('StaSh'):
    def launch_stash():
        bm.ide.run_action('StaSh')

    bm.key_commands.register_key_command(
        'S',
        bm.uikit.UIKeyModifierCommand | bm.uikit.UIKeyModifierShift,
        launch_stash,
        'Launch StaSh')

# Or you can use run_script instead of action to launch StaSh
# if bm.ide.script_exists('launch_stash.py'):
#     def launch_stash():
#         bm.ide.run_script('launch_stash.py')
#
#     bm.key_commands.register_key_command(
#         'S',
#         bm.uikit.UIKeyModifierCommand | bm.uikit.UIKeyModifierShift,
#         launch_stash,
#         'Launch StaSh')
