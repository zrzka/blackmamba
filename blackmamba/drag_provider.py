#!python3

import ui
from objc_util import ObjCClass, ObjCInstance, ns, create_objc_class, ObjCBlock, NSData
import ctypes
import editor
import os
import zipfile
import blackmamba.runtime as runtime
from blackmamba.uikit import UITableViewCellStyle
from blackmamba.key_event import (
    register_key_event_handler, unregister_key_event_handler,
    UIEventKeyCodeLeftSquareBracket, UIEventKeyCodeEscape
)
from blackmamba.key_command import UIKeyModifierControl
from blackmamba.log import error
import blackmamba.ide as ide
import console

_TMP_DIR = os.environ.get('TMPDIR', os.environ.get('TMP'))

NSItemProvider = ObjCClass('NSItemProvider')
UIDragItem = ObjCClass('UIDragItem')
NSError = ObjCClass('NSError')

NSItemProviderRepresentationVisibilityAll = 0

_drag_items = []
_load_data_path = None


def _type_identifier(path):
    if os.path.isdir(path):
        return 'public.folder'
    elif os.path.isfile(path):
        return 'public.data'
    return None


def _suggested_name(path):
    name = os.path.basename(path)

    if os.path.isdir(path):
        name += '.zip'

    return name


def _provide_file_data(path):
    data = NSData.dataWithContentsOfFile_(path)
    if not data:
        error('Failed to read file: {}'.format(path))
        return None

    return data


def _provide_folder_data(path):
    saved_dir = os.getcwd()
    os.chdir(os.path.dirname(path))
    folder_name = os.path.basename(path)

    zip_file_path = os.path.join(_TMP_DIR, '{}.zip'.format(folder_name))

    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)

    ignore_folders = ['.git']
    ignore_files = ['.DS_Store']

    with zipfile.ZipFile(zip_file_path, 'w') as zip:
        for root, subdirs, files in os.walk(folder_name, topdown=True):
            if ignore_folders:
                subdirs[:] = [d for d in subdirs if d not in ignore_folders]
            for file in files:
                if file not in ignore_files:
                    zip.write(os.path.join(root, file))

    os.chdir(saved_dir)

    return _provide_file_data(zip_file_path)


def _provide_data(path):
    if os.path.isfile(path):
        return _provide_file_data(path)
    elif os.path.isdir(path):
        return _provide_folder_data(path)

    return None


def _load_data_imp(_cmd, _block_ptr):
    global _load_data_path
    handler = runtime.ObjCBlockPointer(_block_ptr,
                                       argtypes=[ctypes.c_void_p, ctypes.c_void_p])

    if _load_data_path:
        data = _provide_data(_load_data_path)
        _load_data_path = None
    else:
        data = None

    if not data:
        error = NSError.errorWithDomain_code_userInfo_('com.robertvojta.blackmamba', 1, None)
        handler(None, error)
    else:
        handler(data, None)


_load_data = ObjCBlock(_load_data_imp, restype=ctypes.c_void_p,
                       argtypes=[ctypes.c_void_p, ctypes.c_void_p])


def tableView_itemsForBeginningDragSession_atIndexPath_(_self, _cmd, tv_ptr, session_ptr, index_path_ptr):
    global _load_data_path
    index = ObjCInstance(index_path_ptr).row()

    if index >= 0 and index < len(_drag_items):
        path = _drag_items[index]['path']

        type_identifier = _type_identifier(path)
        if not type_identifier:
            error('Failed to provide data, file does not exists?')
            return ns([]).ptr

        suggested_name = _suggested_name(path)

        provider = NSItemProvider.alloc().init()

        args = [type_identifier, NSItemProviderRepresentationVisibilityAll, _load_data]
        provider.registerDataRepresentationForTypeIdentifier_visibility_loadHandler_(*args)

        if not provider:
            error('Failed to create item provider.')
            return ns([]).ptr

        if suggested_name:
            provider.setSuggestedName(suggested_name)

        item = UIDragItem.alloc().initWithItemProvider_(provider)
        if not item:
            error('Failed to create drag item.')
            return ns([]).ptr

        _load_data_path = path
        return ns([item]).ptr

    return ns([]).ptr


class DragDataSource(ui.ListDataSource):
    def __init__(self, items):
        super().__init__(items)

    def tableview_cell_for_row(self, tableview, section, row):
        item = self.items[row]
        cell = ui.TableViewCell(UITableViewCellStyle.subtitle.value)
        cell.text_label.text = item['title']
        cell.detail_text_label.text = item['subtitle']
        cell.image_view.image = ui.Image(item['image'])
        cell.detail_text_label.text_color = (0, 0, 0, 0.5)
        return cell


class DragView(ui.View):
    def __init__(self, path):
        methods = [tableView_itemsForBeginningDragSession_atIndexPath_]
        protocols = ['UITableViewDragDelegate']
        DragDelegate = create_objc_class('DragDelegate', methods=methods, protocols=protocols)

        self._drag_delegate = DragDelegate.alloc().init()

        self.width = 540
        self.height = 540

        self.ds = DragDataSource(_drag_items)
        self.ds.move_enabled = False
        self.ds.delete_enabled = False

        self.background_color = '#ffffff'

        self.help_label = ui.Label()
        self.help_label.width = self.bounds.width - 12
        self.help_label.height = 32
        self.help_label.x = self.bounds.x + 6
        self.help_label.y = self.bounds.height - self.help_label.height - 3 + self.bounds.x
        self.help_label.text_color = '#484848'
        self.help_label.text = 'Esc - close • Ctrl [ - close with Apple smart keyboard'
        self.help_label.background_color = '#ffffff'
        self.help_label.alignment = ui.ALIGN_CENTER
        self.help_label.font = ('<system>', 13)
        self.add_subview(self.help_label)

        self.tv = ui.TableView()
        self.tv.allows_multiple_selection = False
        self.tv.allows_selection = False
        self.tv.allows_multiple_selection_during_editing = False
        self.tv.allows_selection_during_editing = False
        self.tv.data_source = self.ds
        self.tv.delegate = self.ds
        self.tv.frame = (self.bounds.x, self.bounds.y, self.bounds.width, self.bounds.height - 32 - 18)
        self.add_subview(self.tv)

        tv_objc = ObjCInstance(self.tv)
        tv_objc.setDragDelegate_(self._drag_delegate)

        def handle_escape():
            self.close()

        self._handlers = []
        self._handlers.append(register_key_event_handler(UIEventKeyCodeEscape, handle_escape))
        self._handlers.append(register_key_event_handler(UIEventKeyCodeLeftSquareBracket, handle_escape,
                                                         modifier_flags=UIKeyModifierControl))

    def will_close(self):
        for handler in self._handlers:
            unregister_key_event_handler(handler)


def _drag_path_item(path, root):
    is_folder = os.path.isdir(path)

    breadcrumb = os.path.dirname(path)[len(root) + 1:]
    breadcrumb = ' • '.join(breadcrumb.split(os.path.sep))

    item = {
        'title': os.path.basename(path),
        'subtitle': breadcrumb,
        'image': 'iob:folder_24' if is_folder else 'iob:document_24',
        'folder': is_folder,
        'accessory_type': 'none',
        'path': path,
        'drag_delegate': None
    }
    return item


def _drag_path_items(path):
    docs_path = os.path.normpath(os.path.expanduser('~/Documents'))
    root = os.path.dirname(docs_path)

    items = [_drag_path_item(path, root)]

    while True:
        path = os.path.normpath(os.path.dirname(path))
        if path == docs_path:
            break

        items.append(_drag_path_item(path, root))

    return items


def drag_provider_dialog():
    global _drag_items

    path = editor.get_path()
    if not path:
        console.hud_alert('You have to open file first', 'error', 1.0)
        return

    ide.save(all=True)

    _drag_items = _drag_path_items(path)

    v = DragView(path)
    v.name = 'Drag File or Folder'
    v.present('sheet')
    v.wait_modal()

    _drag_items = []


if __name__ == '__main__':
    drag_provider_dialog()
