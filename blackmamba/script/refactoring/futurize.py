#!python3
"""
Script name ``futurize.py``.

Runs stage 1 of the `futurizer <https://github.com/PythonCharmers/python-future>`_.
"""

import console
import os
import unittest.mock as mock

import blackmamba.ide.source as source
import blackmamba.ide.tab as tab
import editor


_SUFFIX = '3'


def _replace_file_content(path):
    futurized_path = '{}{}'.format(path, _SUFFIX)

    if not os.path.exists(futurized_path):
        # This function is not called unless result is 0, thus if file doesn't
        # exist, we can assume that there's no need to change anything -> success
        return True

    line_number = source.get_line_number()
    content = editor.get_text()

    if not line_number or content is None:
        os.remove(futurized_path)
        return False

    new_content = open(futurized_path, 'r').read()
    editor.replace_text(0, len(content) - 1, new_content)
    source.scroll_to_line(line_number)
    os.remove(futurized_path)
    return True


# I'm lazy one, cripples Pythonista logging
@mock.patch('logging.basicConfig')
def main(mock):
    import libfuturize.main

    path = editor.get_path()
    if not path or not path.endswith('.py'):
        console.hud_alert('Not a Python file', 'error')
        return

    tab.save()
    args = ['-1', '-n', '-w', '--all-imports', '--add-suffix', _SUFFIX, path]

    result = libfuturize.main.main(args)
    if result == 0 and _replace_file_content(path):
        console.hud_alert('Futurized')
    else:
        console.hud_alert('Failed to futurize', 'error')


if __name__ == '__main__':
    from blackmamba.bundle import bundle
    with bundle('refactoring'):
        main()
