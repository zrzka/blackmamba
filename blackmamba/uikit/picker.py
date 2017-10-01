#!python3

import ui
from blackmamba.uikit.table import UITableViewCellStyle
from blackmamba.uikit.keyboard import (
    UIKeyModifier, UIEventKeyCode,
    register_key_event_handler, unregister_key_event_handlers,
    is_in_hardware_keyboard_mode
)
from blackmamba.uikit.autolayout import LayoutProxy


class PickerItem:
    def __init__(self, title, subtitle=None, image=None):
        self._title = title
        self._normalized_title = title.lower()

        self.subtitle = subtitle
        self.image = image
        self.title = title

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, new_value):
        self._title = new_value
        self._normalized_title = new_value.lower() if new_value else None

    @property
    def sort_value(self):
        return self._normalized_title

    @property
    def match_value(self):
        return self._normalized_title

    def matches(self, search_terms):
        if not search_terms:
            return True

        start = 0
        for t in search_terms:
            start = self.match_value.find(t, start)

            if start == -1:
                return False

            start += len(t)

        return True

    def __lt__(self, other):
        return self.sort_value < other.sort_value

    def __str__(self):
        return self.title


class PickerDataSource(object):
    def __init__(self):
        self.tableview = None
        self.action = None
        self._filter_by = None
        self._selected_row = -1
        self._items = None
        self._filtered_items = []
        self._filter = None

    def _filter_items(self):
        if self._filter:
            search_terms = [
                x.strip()
                for x in self._filter.split(' ')
                if x.strip()
            ]

            self._filtered_items = [
                i for i in self._items if i.matches(search_terms)
            ]
        else:
            self._filtered_items = self._items
        self._selected_row = -1
        self.reload()

    def filter_by(self, filter):
        self._filter = filter
        self._filter_items()

    @property
    def filtered_items(self):
        return self._filtered_items

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = value
        self._filter_items()

    @property
    def selected_row(self):
        return self._selected_row

    @selected_row.setter
    def selected_row(self, value):
        if self.tableview:
            self.tableview.selected_row = (0, value)
        self._selected_row = value

    @property
    def selected_item(self):
        if self.selected_row >= 0:
            return self._filtered_items[self.selected_row]
        return None

    def select_next_item(self):
        count = len(self._filtered_items)

        if not count:
            return

        row = (self.selected_row + 1) % count
        self.selected_row = row

    def select_previous_item(self):
        count = len(self._filtered_items)

        if not count:
            return

        row = self.selected_row - 1
        if row < 0:
            row = count - 1

        self.selected_row = row

    def reload(self):
        if self.tableview:
            self.tableview.reload()

    def tableview_number_of_sections(self, tv):
        self.tableview = tv
        return 1

    def tableview_number_of_rows(self, tv, section):
        return len(self._filtered_items)

    def tableview_can_delete(self, tv, section, row):
        return False

    def tableview_can_move(self, tv, section, row):
        return False

    def tableview_did_select(self, tv, section, row):
        self._selected_row = row
        if self.action and row >= 0:
            self.action(self)

    def tableview_cell_for_row(self, tv, section, row):
        item = self._filtered_items[row]
        cell = ui.TableViewCell(UITableViewCellStyle.subtitle.value)
        cell.text_label.number_of_lines = 1
        cell.text_label.text = item.title
        cell.detail_text_label.text = item.subtitle
        cell.detail_text_label.text_color = (0, 0, 0, 0.5)
        if item.image:
            cell.image_view.image = item.image
        return cell


class PickerView(ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if 'background_color' not in kwargs:
            self.background_color = 'white'

        if 'frame' not in kwargs:
            self.width = min(ui.get_window_size()[0] * 0.8, 700)
            self.height = ui.get_window_size()[1] * 0.8

        self._tableview = ui.TableView()
        self._textfield = ui.TextField()
        self._help_label = ui.Label()
        self._datasource = None
        self._handlers = None
        self.shift_enter_enabled = True
        self.did_select_item_action = None

        tf = LayoutProxy(self._textfield)
        self.add_subview(tf)
        tf.layout.align_left_with_superview.equal = 8
        tf.layout.align_top_with_superview.equal = 8
        tf.layout.align_right_with_superview.equal = -8
        tf.layout.height.equal = 31
        tf.delegate = self

        tv = LayoutProxy(self._tableview)
        self.add_subview(tv)
        tv.layout.align_left_to(tf).equal = 0
        tv.layout.align_right_to(tf).equal = 0
        tv.layout.top_offset_to(tf).equal = 8
        tv.allows_selection = True
        tv.allows_multiple_selection = False

        hl = LayoutProxy(self._help_label)
        self.add_subview(hl)
        hl.layout.align_left_to(tv).equal = 0
        hl.layout.align_right_to(tv).equal = 0
        hl.layout.top_offset_to(tv).equal = 8
        hl.layout.align_bottom_with_superview.equal = -8
        hl.layout.height.max = 66
        hl.font = ('<system>', 13.0)
        hl.alignment = ui.ALIGN_CENTER
        hl.text_color = (0, 0, 0, 0.5)
        hl.number_of_lines = 2

        if is_in_hardware_keyboard_mode:
            tf.view.begin_editing()

        self._register_key_event_handlers()

    def _register_key_event_handlers(self):
        def handle_key_up():
            if not self._datasource:
                return

            self._datasource.select_previous_item()

        def handle_key_down():
            if not self._datasource:
                return

            self._datasource.select_next_item()

        def handle_shift_enter():
            if self.shift_enter_enabled:
                self._did_select_item(True)

        def handle_enter():
            self._did_select_item()

        def handle_escape():
            self.close()

        self._handlers = [
            register_key_event_handler(UIEventKeyCode.up, handle_key_up),
            register_key_event_handler(UIEventKeyCode.down, handle_key_down),
            register_key_event_handler(UIEventKeyCode.enter, handle_enter),
            register_key_event_handler(UIEventKeyCode.enter, handle_shift_enter,
                                       modifier=UIKeyModifier.shift),
            register_key_event_handler(UIEventKeyCode.escape, handle_escape),
            register_key_event_handler(UIEventKeyCode.dot, handle_escape,
                                       modifier=UIKeyModifier.command)
        ]

    def will_close(self):
        if self._handlers:
            unregister_key_event_handlers(self._handlers)

    @property
    def datasource(self):
        return self._datasource

    @datasource.setter
    def datasource(self, value):
        self._datasource = value

        def did_select_item(ds):
            self._did_select_item()

        self._datasource.action = did_select_item
        self._tableview.data_source = self._datasource
        self._tableview.delegate = self._datasource

    @property
    def help_label(self):
        return self._help_label

    @property
    def textfield(self):
        return self._textfield

    def _did_select_item(self, shift_enter=False):
        if not self._datasource:
            return

        item = self._datasource.selected_item
        if not item:
            return

        self.close()
        if self.did_select_item_action:
            self.did_select_item_action(item, shift_enter)

    def textfield_should_return(self, textfield):
        return False

    def textfield_should_change(self, textfield, range, replacement):
        if self._datasource:
            string = textfield.text[:range[0]] + replacement + textfield.text[range[1]:]
            self._datasource.filter_by(string)
        return True
