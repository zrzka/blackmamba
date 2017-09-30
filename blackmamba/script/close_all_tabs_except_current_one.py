#!python3
"""
Close all tabs except current one
=================================

* Script name: ``close_all_tabs_except_current_one.py``
* Keyboard shortcut: ``Cmd Shift W``
"""

import blackmamba.ide.tab as tab


def main():
    tab.close_tabs_except_current()


if __name__ == '__main__':
    main()
