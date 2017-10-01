#!python3
"""
Script name ``close_all_tabs_except_current_one.py``.

Closes all tabs except current one.
"""

import blackmamba.ide.tab as tab


def main():
    tab.close_tabs_except_current()


if __name__ == '__main__':
    main()
