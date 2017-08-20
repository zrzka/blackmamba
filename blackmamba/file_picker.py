#!python3

import editor
import os
from objc_util import on_main_thread
from blackmamba.picker import load_picker_view, PickerItem, PickerDataSource
        
                
class FilePickerItem(PickerItem):
    def __init__(self, folder, name, display_folder):
        super().__init__(name, display_folder)
        self._folder = folder
        
    @property
    def file_path(self):
        return os.path.join(self._folder, self.title)


class FilePickerDataSource(PickerDataSource):
    def __init__(self, root_folder=None, allow_folder=None, allow_file=None):
        super().__init__()
        self._root_folder = root_folder or os.path.expanduser('~/Documents')
                
        home_folder = os.path.expanduser('~')
        items = []
        for root, subdirs, files in os.walk(self._root_folder, topdown=True):
            if allow_folder:
                subdirs[:] = [d for d in subdirs if allow_folder(root, d)]
            display_folder = ' • '.join(root[len(home_folder) + 1:].split(os.sep))
            if allow_file:
                files = [f for f in files if allow_file(root, f)]
            items.extend([FilePickerItem(root, f, display_folder) for f in files])
                
        self.items = items
                        

@on_main_thread
def open_quickly():
    def allow_folder(root, folder):
        return folder not in [
                '.git', 'Pythonista', 'site-packages', 'site-packages-2',
                'stash_extensions', 'Examples', '.Trash'            
            ]

    def allow_file(root, name):
        return not name.startswith('.')
        
    def open_file(item, shift_enter):
        new_tab = not shift_enter
        editor.open_file(item.file_path, new_tab=new_tab)        
                                                    
    kwargs = {
        'allow_folder': allow_folder,
        'allow_file': allow_file,        
        'root_folder': os.path.expanduser('~/Documents')
    }
        
    v = load_picker_view()
    v.datasource = FilePickerDataSource(**kwargs)
    v.shift_enter_enabled = True
    v.title_label.text = 'Open Quickly...'
    v.help_label.text = (
        '⇅ - select • Enter - open file in new tab • Shift + Enter - open file in current tab'
        '\n'
        'Esc - close • Ctrl [ - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter files...'
    v.did_select_item_action = open_file
    v.present('sheet', hide_title_bar=True)
    v.wait_modal()
    

if __name__ == '__main__':
    open_quickly()

