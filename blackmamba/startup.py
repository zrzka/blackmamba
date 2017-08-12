#!python3

import blackmamba.toggle_comments
import blackmamba.ide
import blackmamba.file_picker
import blackmamba.dash
from blackmamba.key_commands import *
from blackmamba.uikit import *

def _register_key_commands():
    print('Registering keyboard shortcuts ... ', end='')  
    commands = {
        PYTHONISTA_SCOPE_GLOBAL: [
        ],
        PYTHONISTA_SCOPE_EDITOR: [
            ('/', UIKeyModifierCommand, blackmamba.toggle_comments.toggle_comments, 'Toggle Comments'),
            ('N', UIKeyModifierCommand, blackmamba.ide.new_file, 'New File'),
            ('N', UIKeyModifierCommand | UIKeyModifierShift, blackmamba.ide.new_tab, 'New Tab'),
            ('0', UIKeyModifierCommand, blackmamba.ide.toggle_navigator, 'Toggle Navigator'),
            ('W', UIKeyModifierCommand, blackmamba.ide.close_current_tab, 'Close Tab'),
            ('W', UIKeyModifierCommand | UIKeyModifierShift, blackmamba.ide.close_all_tabs_except_current_one, 'Close Tabs Except Current One'),
            ('O', UIKeyModifierCommand, blackmamba.file_picker.open_quickly, 'Open Quickly'),
            ('0', UIKeyModifierCommand | UIKeyModifierShift, blackmamba.dash.search_dash, 'Search in Dash')
        ]
    }
    
    for scope, commands in commands.items():
        for command in commands:
            register_key_command(scope, *command)
            
    print('done')
            
            
def start():
    print('Black Mamba startup')                
    _register_key_commands()
    print('Black Mamba initialized')

