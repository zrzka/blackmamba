#!python3
"""
Script name ``action_quickly.py``.

Shows dialog with user defined action items (wrench icon). You can filter them
by title, use arrow keys to change selection and run any of them with ``Enter`` key.

Only **user defined action items** are listed.
"""

import os
from ui import TableViewCell
from blackmamba.uikit.picker import PickerView, PickerItem, PickerDataSource
from blackmamba.uikit.table import UITableViewCellStyle
from blackmamba.ide.action import ActionInfo, get_actions


class ActionPickerItem(PickerItem):
    def __init__(self, action_info):
        if not isinstance(action_info, ActionInfo):
            action_info = ActionInfo(action_info)

        if action_info.title:
            title = action_info.title
        else:
            _, tail = os.path.split(action_info.script_name)
            title, _ = os.path.splitext(tail)

        subtitle = ' • '.join(action_info.script_name.split(os.sep))

        super().__init__(title, subtitle)

        self.action_info = action_info


class ActionPickerDataSource(PickerDataSource):
    def __init__(self):
        super().__init__()
        self.items = sorted([ActionPickerItem(ai) for ai in get_actions()])

    def tableview_cell_for_row(self, tv, section, row):
        item = self.filtered_items[row]
        cell = TableViewCell(UITableViewCellStyle.subtitle.value)
        cell.text_label.number_of_lines = 1
        cell.text_label.text = item.title
        cell.detail_text_label.text = item.subtitle
        cell.detail_text_label.text_color = (0, 0, 0, 0.5)
        return cell


def main():
    def run_wrench_item(item, shift_enter):
        item.action_info.run(delay=1.0)

    v = PickerView()
    v.name = 'Action Quickly...'
    v.datasource = ActionPickerDataSource()
    v.shift_enter_enabled = False
    v.help_label.text = (
        '⇅ - select • Enter - run action item'
        '\n'
        'Esc - close • Cmd . - Close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter wrench items...'
    v.did_select_item_action = run_wrench_item
    v.present('sheet')
    v.wait_modal()


if __name__ == '__main__':
    main()
