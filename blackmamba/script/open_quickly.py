#!python3
"""
Script name ``open_quickly.py``.

Shows dialog with all your files. You can filter these files by directories,
file name, etc. Use arrow keys to change selection and then hit ``Enter`` to open
selected file.

If file is already opened, Black Mamba changes selected tab only.

This script is configurable, see :ref:`configuration-file_picker` configuration.
"""

import os
from blackmamba.uikit.picker import PickerView, PickerItem, PickerDataSource
from blackmamba.config import get_config_value
import blackmamba.ide.tab as tab
import blackmamba.ide.bookmark as bookmark


_IGNORE_FOLDERS = {
    '': ['.git'],
    '.': ['.Trash', 'Examples',
          'site-packages', 'site-packages-2', 'site-packages-3']
}


def _ignore_folders():
    return get_config_value('file_picker.ignore_folders', _IGNORE_FOLDERS)


class FilePickerItem(PickerItem):
    def __init__(self, folder, name, display_folder, root_folder=None):
        super().__init__(name, display_folder)
        self._folder = folder
        self._root_folder = root_folder
        self._match_value = None
        self._file_path = None

    @property
    def file_path(self):
        if not self._file_path:
            self._file_path = os.path.join(self._folder, self.title)
        return self._file_path

    @property
    def match_value(self):
        if not self._match_value:
            path = self.file_path
            if self._root_folder:
                path = path[len(self._root_folder)+1:]
            self._match_value = path.lower()

        return self._match_value


class FilePickerDataSource(PickerDataSource):
    def __init__(self, allow_file=None, ignore_folders=None):
        super().__init__()

        items = self._load_items('Documents', os.path.expanduser('~/Documents'), allow_file, ignore_folders)

        bookmarks = bookmark.get_bookmark_paths()
        if bookmarks:
            for path in bookmarks:
                items.extend(self._load_items('Bookmark', path, allow_file, ignore_folders, True))

        self.items = sorted(items)

    def _load_items(self, title, path, allow_file=None, ignore_folders=None, bookmark=False):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        if os.path.isfile(path):
            if allow_file and allow_file(dirname, basename):
                return [FilePickerItem(dirname, basename, '{} • {}'.format(title, basename), dirname)]

        if not os.path.isdir(path):
            return []

        global_ignore_folders = ignore_folders.get('', [])

        items = []
        for root, subdirs, files in os.walk(path, topdown=True, followlinks=True):
            if ignore_folders:
                ignore_list = global_ignore_folders[:]
                ignore_list.extend(ignore_folders.get(os.path.basename(root), []))
                if root == path:
                    ignore_list.extend(ignore_folders.get('.', []))
                subdirs[:] = [d for d in subdirs if d not in ignore_list]

            display_folder_items = [x for x in root[len(path) + 1:].split(os.sep) if x]
            display_folder_items.insert(0, title)
            if bookmark:
                display_folder_items.insert(1, basename)
            display_folder = ' • '.join(display_folder_items)

            if allow_file:
                files = [f for f in files if allow_file(root, f)]

            items.extend([FilePickerItem(root, f, display_folder, path) for f in files])

        return items


def main():
    def allow_file(root, name):
        return not name.startswith('.')

    def open_file(item, shift_enter):
        new_tab = not shift_enter
        tab.open_file(item.file_path, new_tab=new_tab)

    kwargs = {
        'ignore_folders': _ignore_folders(),
        'allow_file': allow_file
    }

    v = PickerView()
    v.name = 'Open Quickly...'
    v.datasource = FilePickerDataSource(**kwargs)
    v.shift_enter_enabled = True
    v.help_label.text = (
        '⇅ - select • Enter - open file in new tab • Shift + Enter - open file in current tab'
        '\n'
        'Esc - close • Cmd . - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter files...'
    v.did_select_item_action = open_file
    v.present('sheet')
    v.wait_modal()


if __name__ == '__main__':
    main()
