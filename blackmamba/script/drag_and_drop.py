#!python3
"""
Script name ``drag_and_drop.py``. **iOS >= 11.0 required**.

Shows dialog with opened files and folders tree. You can drag a file / folder to
any other iOS application. Works well with `Working Copy <http://workingcopyapp.com/>`_
and `Kaleidoscope <https://www.kaleidoscopeapp.com/>`_ for example.

You can drag a file / folder from any other iOS application as well. But there's one
limitation, you can drop them at the folder only.

.. note:: If you drop a folder, folder tree is not refreshed. You have to close
   dialog and open it again to see a new folder. Will be fixed.

This script is configurable, see :ref:`configuration`.
"""

import os
import ui
from objc_util import ns, ObjCClass, ObjCInstance, ObjCBlock, create_objc_class
from blackmamba.log import error
import blackmamba.util.runtime as runtime
import editor
import ctypes
import zipfile
from blackmamba.uikit.keyboard import (
    register_key_event_handler, unregister_key_event_handlers,
    UIEventKeyCode, UIKeyModifier
)
import blackmamba.ide.tab as tab
import console
import io
import shutil
from blackmamba.config import get_config_value

_TMP_DIR = os.environ.get('TMPDIR', os.environ.get('TMP'))

NSIndexPath = ObjCClass('NSIndexPath')
NSItemProvider = ObjCClass('NSItemProvider')
UIDragItem = ObjCClass('UIDragItem')
NSError = ObjCClass('NSError')
NSFileHandle = ObjCClass('NSFileHandle')
UITableViewDropProposal = ObjCClass('UITableViewDropProposal')

_path_items = None
_dragged_item_path = None
_dropped_item_destination_path = None
_dropped_item_is_folder = None
_dropped_item_name = None

#
# Drag support
#


def _type_identifier(path):
    if os.path.isdir(path):
        return 'public.folder'
    elif os.path.isfile(path):
        return 'public.data'
    return None


def _suggested_name(path):
    return os.path.basename(path)


def _load_data_imp(_cmd, _block_ptr):
    global _dragged_item_path
    handler = runtime.ObjCBlockPointer(_block_ptr,
                                       argtypes=[ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p])

    if _dragged_item_path:
        NSURL = ObjCClass('NSURL')
        url = NSURL.fileURLWithPath_isDirectory_(ns(_dragged_item_path), os.path.isdir(_dragged_item_path))

        _dragged_item_path = None
    else:
        url = None

    if not url:
        error = NSError.errorWithDomain_code_userInfo_('com.robertvojta.blackmamba', 1, None)
        handler(None, None, error)
    else:
        handler(url.ptr, False, None)


_load_data = ObjCBlock(_load_data_imp, restype=ctypes.c_void_p,
                       argtypes=[ctypes.c_void_p, ctypes.c_void_p])


def tableView_itemsForBeginningDragSession_atIndexPath_(_self, _cmd, tv_ptr, session_ptr, index_path_ptr):
    global _dragged_item_path

    if not _path_items:
        return ns([]).ptr

    section = ObjCInstance(index_path_ptr).section()
    row = ObjCInstance(index_path_ptr).row()

    if section >= 0 and section < len(_path_items) and row >= 0 and row < len(_path_items[section]):
        path = _path_items[section][row]

        type_identifier = _type_identifier(path)
        if not type_identifier:
            error('Failed to provide data, file does not exists?')
            return ns([]).ptr

        suggested_name = _suggested_name(path)

        provider = NSItemProvider.alloc().init()
        provider.registerFileRepresentationForTypeIdentifier_fileOptions_visibility_loadHandler_(
            type_identifier,
            0,
            0,
            _load_data
        )

        if not provider:
            error('Failed to create item provider.')
            return ns([]).ptr

        if suggested_name:
            provider.setSuggestedName(suggested_name)

        item = UIDragItem.alloc().initWithItemProvider_(provider)
        if not item:
            error('Failed to create drag item.')
            return ns([]).ptr

        _dragged_item_path = path
        return ns([item]).ptr

    return ns([]).ptr

#
# Drop support
#


def tableView_canHandleDropSession_(_self, _cmd, tv_ptr, session_ptr):
    session = ObjCInstance(session_ptr)

    utis = ['public.data', 'public.folder']

    if session.localDragSession():
        # Disallow in-app drag & drop
        return False

    if not session.hasItemsConformingToTypeIdentifiers_(utis):
        # No supported UTIs, disallow drag
        return False

    if session.items().count() > 1:
        # Only one item is supported
        return False

    return True


def tableView_dropSessionDidUpdate_withDestinationIndexPath_(_self, _cmd, tv_ptr, session_ptr, index_path_ptr):
    tv = ObjCInstance(tv_ptr)
    session = ObjCInstance(session_ptr)

    if not index_path_ptr:
        return UITableViewDropProposal.alloc().initWithDropOperation_intent_(0, 3).ptr

    index_path = ObjCInstance(index_path_ptr)

    if len(_path_items) == 2 and index_path.section() == 0:
        return UITableViewDropProposal.alloc().initWithDropOperation_intent_(0, 3).ptr

    # UIDropOperation
    #  - cancel = 0, forbidden = 1, copy = 2, move = 3
    #
    # UITableViewDropIntent
    #  - unspecified = 0, InsertAtDestinationIndexPath = 1
    #  - InsertIntoDestinationIndexPath = 2, Automatic = 3

    if tv.hasActiveDrag():
        if session.items.count > 1:
            return UITableViewDropProposal.alloc().initWithDropOperation_intent_(0, 3).ptr
        else:
            return UITableViewDropProposal.alloc().initWithDropOperation_intent_(2, 2).ptr
    else:
        return UITableViewDropProposal.alloc().initWithDropOperation_intent_(2, 2).ptr


def _drop_folder(data_ptr, path):
    try:
        if os.path.exists(path):
            console.alert(
                '{} exists'.format(os.path.basename(path)),
                'Do you want to replace existing {}?'.format(
                    'folder' if os.path.isdir(path) else 'file'
                ),
                'Replace'
            )

            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

        data = ObjCInstance(data_ptr)
        zip_data = io.BytesIO(ctypes.string_at(data.bytes(), data.length()))
        zf = zipfile.ZipFile(zip_data)

        corrupted_file = zf.testzip()
        if corrupted_file:
            console.hud_alert('Corrupted ZIP file', 'error')

        zf.extractall(os.path.dirname(path))

        console.hud_alert('{} dropped'.format(os.path.basename(path)))

    except KeyboardInterrupt:
        pass


def _drop_file(data_ptr, path):
    try:
        if os.path.exists(path):
            console.alert(
                '{} exists'.format(os.path.basename(path)),
                'Do you want to replace existing file?',
                'Replace'
            )
        data = ObjCInstance(data_ptr)

        if not data.writeToFile_atomically_(ns(path), True):
            console.hud_alert('Failed to write file', 'error')
            return

        console.hud_alert('{} dropped'.format(os.path.basename(path)))

    except KeyboardInterrupt:
        pass


def _load_dropped_data_imp(_cmd, data_ptr, error_ptr):
    global _dropped_item_destination_path, _dropped_item_is_folder, _dropped_item_name

    if error_ptr or not _dropped_item_destination_path or not _dropped_item_name or _dropped_item_is_folder is None:
        console.hud_alert('Drop operation failed', 'error')
        _dropped_item_destination_path = None
        _dropped_item_is_folder = None
        _dropped_item_name = None
        return

    if _dropped_item_is_folder:
        _drop_folder(
            data_ptr,
            os.path.join(str(_dropped_item_destination_path), str(_dropped_item_name))
        )
    else:
        _drop_file(
            data_ptr,
            os.path.join(str(_dropped_item_destination_path), str(_dropped_item_name))
        )

    _dropped_item_destination_path = None
    _dropped_item_is_folder = None
    _dropped_item_name = None


_load_dropped_data = ObjCBlock(_load_dropped_data_imp, restype=None,
                               argtypes=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p])


def tableView_performDropWithCoordinator_(_self, _cmd, tv_ptr, coordinator_ptr):
    global _dropped_item_destination_path, _dropped_item_is_folder, _dropped_item_name

    coordinator = ObjCInstance(coordinator_ptr)

    index_path = coordinator.destinationIndexPath()
    if not index_path:
        return

    session = coordinator.session()

    for item in session.items():
        provider = item.itemProvider()
        name = provider.suggestedName()

        if not name:
            continue

        folder = provider.hasItemConformingToTypeIdentifier('public.folder')

        if not folder and not provider.hasItemConformingToTypeIdentifier('public.data'):
            continue

        _dropped_item_destination_path = _path_items[index_path.section()][index_path.row()]
        _dropped_item_is_folder = folder
        _dropped_item_name = name

        provider.loadDataRepresentationForTypeIdentifier_completionHandler_(
            'public.folder' if folder else 'public.data',
            _load_dropped_data
        )

#
# UI
#


class FileNode:
    def __init__(self, path, parent=None):
        assert(parent is None or isinstance(parent, FileNode))

        self.path = os.path.normpath(path)
        self.parent = parent
        self.level = parent.level + 1 if parent else 0
        self.name = os.path.basename(path)
        self.children = []

    def add_child(self, child):
        assert(isinstance(child, FileNode))
        self.children.append(child)

    def dump(self):
        print('{} {}'.format(self.level * '  ', os.path.basename(self.path)))
        for child in self.children:
            child.dump()


def build_folder_tree(folder, parent=None, ignore=None):
    node = FileNode(folder, parent=parent)

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        if not os.path.isdir(path):
            continue

        if ignore and ignore(folder, file):
            continue

        child_node = build_folder_tree(path, node, ignore)
        node.add_child(child_node)

    return node


def ignore(folder, file):
    if file.startswith('.'):
        return True

    ignore_folders = get_config_value('drag_and_drop.ignore_folders', None)
    if not ignore_folders:
        return False

    for parent, folders in ignore_folders.items():
        if not parent and file in folders:
            return True

        if parent == '.' and folder == os.path.expanduser('~/Documents') and file in folders:
            return True

        if parent == os.path.basename(folder) and file in folders:
            return True

    return False


class FolderPickerDataSource:
    def __init__(self, root_node, expanded_folder=None, files=None):
        assert(isinstance(root_node, FileNode))
        assert(root_node.level == 0)

        self.tableview = None
        self._root_node = root_node
        self._items = None

        self._files = [
            {
                'title': os.path.basename(file),
                'level': 0,
                'path': file
            }
            for file in files or []
        ]

        if self._files:
            self._file_section = 0
            self._folder_section = 1
        else:
            self._file_section = -1
            self._folder_section = 0

        self._expanded_node_paths = set((root_node.path,))
        if expanded_folder:
            sentinel = os.path.expanduser('~/Documents')

            if not expanded_folder.startswith(sentinel):
                raise ValueError('expanded_folder must start with ~/Documents')

            path = expanded_folder
            while not path == sentinel:
                self._expanded_node_paths.add(path)
                path = os.path.dirname(path)

        self._update_path_items()

    def _update_path_items(self):
        global _path_items

        _file_drag_items = [f['path'] for f in self._files]
        _folder_drag_items = [f['path'] for f in self.items]

        if _file_drag_items:
            _path_items = [_file_drag_items, _folder_drag_items]
        else:
            _path_items = [_folder_drag_items]

    def _node_dict(self, node):
        return {
            'title': os.path.basename(node.path),
            'level': node.level,
            'path': node.path,
            'node': node
        }

    def _generate_node_children_items(self, node):
        items = []

        if not node.children:
            return items

        if node.path not in self._expanded_node_paths:
            return items

        for child in node.children:
            items.append(self._node_dict(child))
            items.extend(self._generate_node_children_items(child))

        return items

    def _generate_node_items(self, node):
        items = [self._node_dict(node)]
        items.extend(self._generate_node_children_items(node))
        return items

    @property
    def items(self):
        if self._items is not None:
            return self._items

        self._items = self._generate_node_items(self._root_node)
        return self._items

    def tableview_title_for_header(self, tv, section):
        if section == self._file_section:
            return 'Editor file (drag only)'
        return 'Folders (drag & drop)'

    def tableview_number_of_sections(self, tv):
        self.tableview = tv
        return self._folder_section + 1

    def tableview_number_of_rows(self, tv, section):
        if section == self._file_section:
            return len(self._files)
        else:
            return len(self.items)

    def tableview_can_delete(self, tv, section, row):
        return False

    def tableview_can_move(self, tv, section, row):
        return False

    def tableview_did_select(self, tv, section, row):
        tv_objc = ObjCInstance(tv)
        index_path = tv_objc.indexPathForSelectedRow()

        if section == self._file_section:
            tv_objc.deselectRowAtIndexPath_animated_(index_path, True)
            return

        item = self.items[row]
        node = item.get('node', None)

        if node.path == self._root_node.path or not node.children:
            tv_objc.deselectRowAtIndexPath_animated_(index_path, True)
            return

        tv_objc.beginUpdates()
        start_index = row + 1
        try:
            self._expanded_node_paths.remove(node.path)

            index_paths = []
            for index, item in enumerate(self._items[start_index:]):
                if item['node'].path.startswith(node.path):
                    index_paths.append(NSIndexPath.indexPathForRow_inSection_(start_index + index, section))
                else:
                    break

            if index_paths:
                self._items[start_index:start_index + len(index_paths)] = []
                tv_objc.deleteRowsAtIndexPaths_withRowAnimation_(ns(index_paths), 3)

        except KeyError:
            self._expanded_node_paths.add(node.path)
            child_items = self._generate_node_children_items(node)

            index_paths = []
            for i in range(start_index, start_index + len(child_items)):
                index_paths.append(NSIndexPath.indexPathForRow_inSection_(i, section))

            self._items[start_index:start_index] = child_items
            tv_objc.insertRowsAtIndexPaths_withRowAnimation_(ns(index_paths), 3)

        tv_objc.reloadRowsAtIndexPaths_withRowAnimation_(ns([index_path]), 5)
        tv_objc.endUpdates()
        self._update_path_items()

    def tableview_cell_for_row(self, tv, section, row):
        if section == self._folder_section:
            item = self.items[row]
            node = item['node']
        else:
            item = self._files[row]
            node = None

        cell = ui.TableViewCell()

        cvb = cell.content_view.bounds

        x = 15 + cvb.x + item['level'] * 15

        if node and node.children:
            image_view = ui.ImageView()
            image_view.frame = (x, 10, 24, 24)
            image_view.image = ui.Image.named(
                'iob:arrow_down_b_24' if node.path in self._expanded_node_paths else 'iob:arrow_right_b_24'
            )
            cell.content_view.add_subview(image_view)

        x += 24 + 8

        image_view = ui.ImageView()
        image_view.frame = (x, 10, 24, 24)
        image_view.image = ui.Image.named('iob:folder_24' if node else 'iob:document_24')
        cell.content_view.add_subview(image_view)

        x += 24 + 8

        title_label = ui.Label(flex='W')
        title_label.text = item['title']
        title_label.size_to_fit()
        title_label.frame = (
            x, cvb.y + (cvb.height - title_label.height) / 2.0,
            cvb.width - (x - cvb.x) - 8, title_label.height
        )
        cell.content_view.add_subview(title_label)

        separator = ui.View(flex='W')
        separator.background_color = (0, 0, 0, 0.05)
        x = title_label.frame.x - 12 - 8
        separator.frame = (
            x, cvb.y + cvb.height - 1,
            cvb.width - (x - cvb.x), 1
        )
        cell.content_view.add_subview(separator)

        cell_objc = ObjCInstance(cell)
        cell_objc.setSelectionStyle(0)

        return cell


class DragAndDropView(ui.View):
    def __init__(self):
        self.name = 'Drag & Drop'

        self.width = min(ui.get_window_size()[0] * 0.8, 700)
        self.height = ui.get_window_size()[1] * 0.8

        path = editor.get_path()
        if path:
            expanded_folder = os.path.dirname(path)
            files = tab.get_paths()
        else:
            expanded_folder = None
            files = None

        root_node = build_folder_tree(os.path.expanduser('~/Documents'), ignore=ignore)
        data_source = FolderPickerDataSource(root_node, expanded_folder, files)

        tv = ui.TableView(frame=self.bounds, flex='WH')
        tv.delegate = data_source
        tv.data_source = data_source
        tv.allows_multiple_selection = False
        tv.allows_selection = True
        tv.allows_multiple_selection_during_editing = False
        tv.allows_selection_during_editing = False
        tv.separator_color = 'clear'
        self.add_subview(tv)

        methods = [tableView_itemsForBeginningDragSession_atIndexPath_]
        protocols = ['UITableViewDragDelegate']
        DragDelegate = create_objc_class('DragDelegate', methods=methods, protocols=protocols)
        self._drag_delegate = DragDelegate.alloc().init()

        methods = [
            tableView_canHandleDropSession_,
            tableView_dropSessionDidUpdate_withDestinationIndexPath_,
            tableView_performDropWithCoordinator_
        ]
        protocols = ['UITableViewDropDelegate']
        DropDelegate = create_objc_class('DropDelegate', methods=methods, protocols=protocols)
        self._drop_delegate = DropDelegate.alloc().init()

        tv_objc = ObjCInstance(tv)
        tv_objc.setDragDelegate_(self._drag_delegate)
        tv_objc.setDropDelegate_(self._drop_delegate)

        def handle_escape():
            self.close()

        self._handlers = [
            register_key_event_handler(UIEventKeyCode.escape, handle_escape),
            register_key_event_handler(UIEventKeyCode.dot, handle_escape,
                                       modifier=UIKeyModifier.command)
        ]

    def will_close(self):
        if self._handlers:
            unregister_key_event_handlers(self._handlers)


def main():
    tab.save(True)
    view = DragAndDropView()
    view.present('sheet')


if __name__ == '__main__':
    main()
