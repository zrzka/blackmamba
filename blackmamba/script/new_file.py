#!python3
"""
Script name ``new_file.py``.

If there's no opened file in the Pythonista, new tab is created and *New File...*
button tap is emulated.

Otherwise dialog appears where you can enter new file name. File will be created
in the current folder. If it already exists, file will be opened instead of creating
new one.
"""

import blackmamba.ide.tab as tab
import editor
import os
import console


def main():
    path = editor.get_path()

    if not path:
        tab.new_file()
        return

    folder = os.path.dirname(path)
    try:
        file_name = console.input_alert('Enter filename').strip()

        if not file_name:
            raise KeyboardInterrupt

        path = os.path.join(folder, file_name)
        if os.path.exists(path):
            editor.open_file(path, new_tab=True)
        else:
            editor.make_new_file(path, new_tab=True)

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
