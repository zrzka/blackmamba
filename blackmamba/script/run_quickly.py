#!python3
"""
Script name ``run_quickly.py``.

Shows dialog with all your Python files. You can filter these files by directories,
file name, etc. Use arrows keys to change selection and then hit ``Enter`` to
run selected file.

This script is configurable, see :ref:`configuration`.
"""

import os
from blackmamba.uikit.picker import PickerView, PickerItem, PickerDataSource
import blackmamba.ide.script as script
from blackmamba.config import get_config_value
import blackmamba.util.path as path


_IGNORE_FOLDERS = {
    '': ['.git'],
    '.': ['.Trash', 'Examples',
          'site-packages', 'site-packages-2', 'site-packages-3']
}


def _ignore_folders():
    return get_config_value('file_picker.ignore_folders', _IGNORE_FOLDERS)


class FilePickerItem(PickerItem):
    def __init__(self, folder, name, display_folder):
        super().__init__(name, display_folder)
        self._folder = folder

    @property
    def file_path(self):
        return os.path.join(self._folder, self.title)

    @property
    def match_value(self):
        return path.strip_documents_folder(self.file_path).lower()


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


def main():
    def allow_file(root, name):
        return path.is_python_file(name) and not name.startswith('.')

    def run_script(item, shift_enter):
        script.run_script(item.file_path, full_path=True, delay=1.0)

    kwargs = {
        'ignore_folders': _ignore_folders(),
        'allow_file': allow_file
    }

    v = PickerView()
    v.name = 'Run Quickly...'
    v.datasource = FilePickerDataSource(**kwargs)
    v.shift_enter_enabled = False
    v.help_label.text = (
        '⇅ - select • Enter - run Python script'
        '\n'
        'Esc - close • Cmd . - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter scripts...'
    v.did_select_item_action = run_script
    v.present('sheet')
    v.wait_modal()


if __name__ == '__main__':
    main()
