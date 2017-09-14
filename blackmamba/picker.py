#!python3

from ui import View, load_view, TableViewCell
from blackmamba.uikit import UITableViewCellStyle
from blackmamba.key_command import UIKeyModifierShift, UIKeyModifierControl
from blackmamba.key_event import (
    register_key_event_handler, unregister_key_event_handler,
    UIEventKeyCodeUp, UIEventKeyCodeDown,
    UIEventKeyCodeEnter, UIEventKeyCodeEscape,
    UIEventKeyCodeLeftSquareBracket
)
from blackmamba.keyboard import is_in_hardware_keyboard_mode


class PickerItem(object):
    def __init__(self, title, subtitle=None, image=None):
        self.title = title
        self.subtitle = subtitle
        self.image = image
        self._norm_title = title.lower()

    def matches_title(self, terms):
        if not terms:
            return True

        start = 0
        for t in terms:
            start = self._norm_title.find(t, start)

            if start == -1:
                return False

            start += len(t)

        return True

    def __lt__(self, other):
        return self.title < other.title

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
            self._filtered_items = [
                i for i in self._items if i.matches_title(self._filter)
            ]
        else:
            self._filtered_items = self._items
        self._selected_row = -1
        self.reload()

    def filter_by(self, filter):
        new_filter = [s for s in filter.strip().lower().split(' ') if s]
        self._filter = new_filter
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
        cell = TableViewCell(UITableViewCellStyle.subtitle.value)
        cell.text_label.number_of_lines = 1
        cell.text_label.text = item.title
        cell.detail_text_label.text = item.subtitle
        cell.detail_text_label.text_color = (0, 0, 0, 0.5)
        if item.image:
            cell.image_view.image = item.image
        return cell


class PickerView(View):
    def __init__(self):
        self._tableview = None
        self._textfield = None
        self._help_label = None
        self._datasource = None
        self._handlers = []
        self.shift_enter_enabled = True
        self.did_select_item_action = None
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

        self._handlers.append(register_key_event_handler(UIEventKeyCodeUp, handle_key_up))
        self._handlers.append(register_key_event_handler(UIEventKeyCodeDown, handle_key_down))
        self._handlers.append(register_key_event_handler(UIEventKeyCodeEnter, handle_enter))
        self._handlers.append(register_key_event_handler(UIEventKeyCodeEnter, handle_shift_enter,
                                                         modifier_flags=UIKeyModifierShift))
        self._handlers.append(register_key_event_handler(UIEventKeyCodeEscape, handle_escape))
        self._handlers.append(register_key_event_handler(UIEventKeyCodeLeftSquareBracket, handle_escape,
                                                         modifier_flags=UIKeyModifierControl))

    def will_close(self):
        for handler in self._handlers:
            unregister_key_event_handler(handler)

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

    def did_load(self):
        self._tableview = self['tableview']
        self._textfield = self['textfield']
        self._help_label = self['helplabel']

        self._tableview.allows_selection = True
        self._tableview.allows_multiple_selection = False
        self._textfield.delegate = self

        if is_in_hardware_keyboard_mode:
            self._textfield.begin_editing()

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


def load_picker_view():
    return load_view()
