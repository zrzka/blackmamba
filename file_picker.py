
import editor
import os
from objc_util import *
from ui import *
from uikit import *
import console
from key_events import register_key_event_handler, unregister_key_event_handler
import tabs
        
EXCLUDE_FOLDERS = set(['.git', 'Pythonista', 'site-packages', 'site-packages-2', 'stash_extensions'])
ROOT_FOLDER = os.path.expanduser('~/Documents')
        
class FilePickerListItem(object):
    def __init__(self, folder, name, display_folder):
        self.folder = folder
        self.name = name
        self.norm_name = name.lower()
        self.display_folder = display_folder
        
    @property
    def file_path(self):
        return os.path.join(self.folder, self.name)

    def matches(self, search_terms):
        if not search_terms:
            return True
            
        for st in search_terms:
            if st not in self.norm_name:
                return False
        
        return True

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return self.name
                

class FilePickerDataSource(object):
    def __init__(self):
        self.tableview = None
        self.action = None
        self._filter_by = None
        self._selected_row = -1
        self._items = None
                
        home_folder = os.path.expanduser('~')
        items = []
        for root, subdirs, files in os.walk(ROOT_FOLDER, topdown=True):
            subdirs[:] = [d for d in subdirs if d not in EXCLUDE_FOLDERS]
            display_folder = ' • '.join(root[len(home_folder) + 1:].split(os.sep))
            items.extend([FilePickerListItem(root, f, display_folder) for f in files if not f.startswith('.')])
            
        self._all_items = sorted(items)
        self.filter_by = ''
                
    @property
    def filter_by(self):
        return self._filter_by
        
    @filter_by.setter
    def filter_by(self, value):
        new_filter_by = [s for s in value.strip().lower().split(' ') if s]
        
        self._filter_by = new_filter_by
        
        if self._filter_by:
            self._items = [i for i in self._all_items if i.matches(self._filter_by)]
        else:
            self._items = self._all_items
        self._selected_row = -1
        self.reload()
                                
    @property
    def items(self):
        return self._items
        
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
            return self.items[self.selected_row]
        return None
        
    def select_next_item(self):
        count = len(self.items)
        
        if not count:
            return
            
        row = (self.selected_row + 1) % count
        self.selected_row = row
            
    def select_previous_item(self):
        count = len(self.items)
        
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
        return len(self.items)

    def tableview_can_delete(self, tv, section, row):
        return False

    def tableview_can_move(self, tv, section, row):
        return False
        
    def tableview_did_select(self, tv, section, row):
        self._selected_row = row
        if self.action and row >= 0:
            self.action(self)
            
    def tableview_cell_for_row(self, tv, section, row):
        item = self.items[row]
        cell = TableViewCell(UITableViewCellStyleSubtitle)
        cell.text_label.number_of_lines = 1
        cell.text_label.text = item.name
        cell.detail_text_label.text = item.display_folder
        cell.detail_text_label.text_color = (0, 0, 0, 0.5)
        return cell


class FilePickerView(View):
    def __init__(self):
        self.tv = None
        self.tf = None

        self.ds = FilePickerDataSource()
                
        def did_select_cell(datasource):
            self._open_selected_file()
            
        self.ds.action = did_select_cell
        
        def handle_key_up():
            self.ds.select_previous_item()
            
        def handle_key_down():
            self.ds.select_next_item()
            
        def handle_shift_enter():
            self._open_selected_file(False)
            
        def handle_enter():
            self._open_selected_file()
            
        def handle_escape():
            self.close()
            
        self.key_up_handler = register_key_event_handler(UIEventKeyCodeUp, handle_key_up)
        self.key_down_handler = register_key_event_handler(UIEventKeyCodeDown, handle_key_down)
        self.enter_handler = register_key_event_handler(UIEventKeyCodeEnter, handle_enter)
        self.shift_enter_handler = register_key_event_handler(UIEventKeyCodeEnter, handle_shift_enter, modifier_flags=UIKeyModifierShift)
        self.escape_handler = register_key_event_handler(UIEventKeyCodeEscape, handle_escape)     
        self.escape_handler2 = register_key_event_handler(UIEventKeyCodeLeftSquareBracket, handle_escape, modifier_flags=UIKeyModifierControl)   
            
    def will_close(self):
        unregister_key_event_handler(self.key_up_handler)
        unregister_key_event_handler(self.key_down_handler)
        unregister_key_event_handler(self.enter_handler)
        unregister_key_event_handler(self.shift_enter_handler)        
        unregister_key_event_handler(self.escape_handler)
        unregister_key_event_handler(self.escape_handler2)

    def did_load(self):
        self.tv = self['tableview']
        self.tf = self['textfield']

        self.tv.data_source = self.ds
        self.tv.delegate = self.ds
        self.tv.allows_multiple_selection = False
        self.tf.delegate = self
            
        UITextField = ObjCClass('UITextField')
        tf = ObjCInstance(self.tf._objc_ptr)
        for sv in tf.subviews():
            if sv.isKindOfClass_(UITextField):
                sv.becomeFirstResponder()
                                       
    def _open_selected_file(self, new_tab=True):        
        item = self.ds.selected_item
        if not item:
            return
            
        self.close()
        
        tabs_vc = tabs.tabs_view_controller()
        tabs_vc.openFile_inNewTab_withPreferredEditorType_forceReload_(ns(item.file_path), new_tab, 0, True)
    
    def textfield_should_return(self, textfield):
        return False
        
    def textfield_should_change(self, textfield, range, replacement):
        self.ds.filter_by = textfield.text[:range[0]] + replacement + textfield.text[range[1]:]
        return True


@on_main_thread
def open_quickly():
    v = load_view() # os.path.splitext(inspect.stack()[0][1])[0] + '.pyui')
    v.present('sheet', hide_title_bar=True)
    v.wait_modal()

