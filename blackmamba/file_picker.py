#!python3

import editor
import os
from objc_util import on_main_thread
from blackmamba.picker import load_picker_view, PickerItem, PickerDataSource
import blackmamba.ide as ide


ignore_folders = {
    '': ['.git'],
    '.': ['.Trash', 'Examples',
          'site-packages', 'site-packages-2', 'site-packages-3']
}


class FilePickerItem(PickerItem):
    def __init__(self, folder, name, display_folder):
        super().__init__(name, display_folder)
        self._folder = folder

    @property
    def file_path(self):
        return os.path.join(self._folder, self.title)


class FilePickerDataSource(PickerDataSource):
    def __init__(self, allow_file=None, ignore_folders=None):
        super().__init__()
        self._root_folder = os.path.expanduser('~/Documents')

        def expand_folder(f):
            if not f:
                return f

            return os.path.normpath(os.path.join(self._root_folder, f))

        ignore_folders = {expand_folder(k): v for k, v in ignore_folders.items()}
        global_ignore_folders = ignore_folders.get('', [])

        home_folder = os.path.expanduser('~')
        items = []
        for root, subdirs, files in os.walk(self._root_folder, topdown=True, followlinks=True):
            if ignore_folders:
                ignore_list = global_ignore_folders[:]
                ignore_list.extend(ignore_folders.get(root, []))
                subdirs[:] = [d for d in subdirs if d not in ignore_list]
            display_folder = ' • '.join(root[len(home_folder) + 1:].split(os.sep))
            if allow_file:
                files = [f for f in files if allow_file(root, f)]
            items.extend([FilePickerItem(root, f, display_folder) for f in files])

        self.items = sorted(items)


@on_main_thread
def open_quickly():
    def allow_file(root, name):
        return not name.startswith('.')

    def open_file(item, shift_enter):
        new_tab = not shift_enter
        editor.open_file(item.file_path, new_tab=new_tab)

    kwargs = {
        'ignore_folders': ignore_folders,
        'allow_file': allow_file
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


@on_main_thread
def script_quickly():
    def allow_file(root, name):
        return not name.startswith('.') and name.endswith('.py')

    def run_script(item, shift_enter):
        ide.run_script(item.file_path, full_path=True)

    kwargs = {
        'ignore_folders': ignore_folders,
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
