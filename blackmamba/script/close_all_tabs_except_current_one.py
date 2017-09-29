#!python3

import blackmamba.ide.tab as tab


def close_all_tabs_except_current_one():
    tab.close_tabs_except_current()


if __name__ == '__main__':
    close_all_tabs_except_current_one()
