#!python3

import blackmamba as bm

# ''           : any parent folder
# '.'          : ~/Documents parent folder
# 'Development': ~/Documents/Development parent folder

bm.file_picker.ignore_folders = {
    '': ['.git'],
    '.': ['Pythonista', '.Trash', 'Examples',
          'site-packages-2', 'site-packages', 'stash_extensions'],
    'site-packages-3': ['blackmamba'],
    'Development': ['bm-pip-backup']
}

bm.analyzer.hud_alert_delay = 1.0
bm.analyzer.ignore_codes = None
bm.analyzer.max_line_length = 127
bm.analyzer.remove_whitespaces = True

bm.experimental.tester.hud_alert_delay = 1.0
bm.experimental.tester.hide_console = True

bm.main()

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
