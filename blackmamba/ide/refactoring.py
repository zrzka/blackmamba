#!python3

from difflib import unified_diff

import editor
import ui
from blackmamba.uikit.keyboard import (
    UIKeyModifier, UIEventKeyCode,
    register_key_event_handler, unregister_key_event_handlers
)
from objc_util import ObjCClass, ObjCInstance, on_main_thread


NSMutableAttributedString = ObjCClass('NSMutableAttributedString')
NSAttributedString = ObjCClass('NSAttributedString')
UIColor = ObjCClass('UIColor')
UIFont = ObjCClass('UIFont')


def _change_set_diff(change_set):
    diff = []

    for change in change_set.changes:
        new = change.new_contents
        old = change.old_contents
        if old is None:
            if change.resource.exists():
                old = change.resource.read()
            else:
                old = ''
        result = unified_diff(
            old.splitlines(True), new.splitlines(True),
            'a/' + change.resource.path, 'b/' + change.resource.path
        )
        diff.extend(list(result))
        diff.append('\n')

    return diff


def _diff_to_attributed_string(diff):
    font = UIFont.fontWithName_size_('Menlo', 15.0)

    default_attributes = {'NSFont': font, 'NSColor': UIColor.blackColor()}
    removed_attributes = {'NSFont': font, 'NSBackgroundColor': UIColor.redColor().colorWithAlphaComponent_(0.1)}
    added_attributes = {'NSFont': font, 'NSBackgroundColor': UIColor.greenColor().colorWithAlphaComponent_(0.1)}
    header_attributes = {'NSFont': font, 'NSColor': UIColor.lightGrayColor()}
    range_attributes = {'NSFont': font, 'NSColor': UIColor.lightGrayColor()}

    result = NSMutableAttributedString.alloc().init()

    for line in diff:
        attributes = default_attributes
        if line.startswith('---') or line.startswith('+++'):
            attributes = header_attributes
        elif line.startswith('@@'):
            attributes = range_attributes
        elif line.startswith('+'):
            attributes = added_attributes
        elif line.startswith('-'):
            attributes = removed_attributes

        line_string = NSAttributedString.alloc().initWithString_attributes_(line, attributes)
        result.appendAttributedString_(line_string)

    return result


@on_main_thread
def _set_attributed_text(textview, attributed_string):
    tv_objc = ObjCInstance(textview)
    tv_objc.setAttributedText_(attributed_string)


class _PreviewChangesView(ui.View):
    def __init__(self, change_set, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'Preview'
        self.apply_changes = False

        def apply(sender):
            self.apply_changes = True
            self.close()

        button = ui.ButtonItem('Apply', action=apply)
        self.right_button_items = [button]

        textview = ui.TextView(frame=self.bounds, flex='WH')
        textview.editable = False

        diff = _change_set_diff(change_set)
        attributed_string = _diff_to_attributed_string(diff)
        _set_attributed_text(textview, attributed_string)

        self.add_subview(textview)

        def cancel():
            self.close()

        self.handlers = [
            register_key_event_handler(UIEventKeyCode.ESCAPE, cancel),
            register_key_event_handler(UIEventKeyCode.DOT, cancel, modifier=UIKeyModifier.COMMAND),
            register_key_event_handler(UIEventKeyCode.ENTER, lambda: apply(None))
        ]

    def will_close(self):
        unregister_key_event_handlers(self.handlers)


def ask_if_apply_change_set(change_set):
    if not change_set:
        return False

    view = _PreviewChangesView(change_set)
    view.present('fullscreen')
    view.wait_modal()

    return view.apply_changes


def apply_change_set(change_set, path=None, initial_selection=None):
    #
    # Why not project.do(change_set)?
    #
    #  - iCloud, Files, ... - there're special functions to update files, not a simple file system
    #  - we have to be sure just one file (= opened) is updated only, because of Pythonista reloading, ...
    #
    for change in change_set.changes:
        if path and not change.resource.real_path == path:
            # Make sure we modify opened file only
            continue

        if path and not path == editor.get_path():
            # Make sure that user didn't switch tab, close tab, ...
            continue

        end = len(editor.get_text()) - 1
        editor.replace_text(0, end, change.new_contents)
        if initial_selection:
            editor.set_selection(*initial_selection, scroll=True)
