#!python3

import blackmamba as bm

################################################################
# Default Black Mamba external keyboard shortcuts registration #
################################################################

bm.register_default_key_commands()


################################################################
# Open/Run Quickly... ignore folders                           #
################################################################

# ''           : any parent folder
# '.'          : ~/Documents parent folder
# 'Development': ~/Documents/Development parent folder

bm.settings.OPEN_QUICKLY_IGNORE_FOLDERS = {
    '': ['.git'],
    '.': ['Pythonista', '.Trash', 'Examples',
          'site-packages-2', 'site-packages', 'stash_extensions'],
    'site-packages-3': ['blackmamba'],
    'Development': ['bm-pip-backup']
}

bm.settings.RUN_QUICKLY_IGNORE_FOLDERS = {
    '': ['.git'],
    '.': ['Pythonista', '.Trash', 'Examples',
          'site-packages-2', 'site-packages', 'stash_extensions'],
    'site-packages-3': ['blackmamba'],
    'Development': ['bm-pip-backup']
}


################################################################
# Analyzer                                                     #
################################################################

# Must be None or tuple ('W391', 'W293', ...)
bm.settings.ANALYZER_PEP8_IGNORE = None

# Max line length (E501)
# 127 is the GitHub editor max line length
bm.settings.ANALYZER_PEP8_MAX_LINE_LENGTH = 127


################################################################
# Unit tests                                                   #
################################################################

bm.settings.TESTS_HUD_DELAY = 1.0
bm.settings.TESTS_HIDE_CONSOLE = True

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
