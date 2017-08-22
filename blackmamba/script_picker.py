#!python3

import os
from objc_util import on_main_thread
from blackmamba.picker import load_picker_view
from blackmamba.file_picker import FilePickerDataSource
import blackmamba.ide
import blackmamba.settings        

@on_main_thread
def script_quickly():
    def allow_file(root, name):
        return not name.startswith('.') and name.endswith('.py')
        
    def run_script(item, shift_enter):
        blackmamba.ide.run_script(item.file_path)
                                                    
    kwargs = {
        'ignore_folders': blackmamba.settings.RUN_QUICKLY_IGNORE_FOLDERS,
        'allow_file': allow_file
    }
        
    v = load_picker_view()
    v.datasource = FilePickerDataSource(**kwargs)
    v.shift_enter_enabled = False
    v.title_label.text = 'Run Quickly...'
    v.help_label.text = (
        '⇅ - select • Enter - run Python script'
        '\n'
        'Esc - close • Ctrl [ - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter scripts...'
    v.did_select_item_action = run_script
    v.present('sheet', hide_title_bar=True)
    v.wait_modal()
    

if __name__ == '__main__':
    script_quickly()

