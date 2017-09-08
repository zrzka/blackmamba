#!python3

from objc_util import on_main_thread, ObjCInstance, sel, UIApplication
from blackmamba.runtime import swizzle
import blackmamba.system as system

# UIEventType
#
# UIEventTypePhysicalKeyboard is not publicly defined in the UIKit. I just
# added it here so I can use it in events.

_UIEventTypeTouches = 0
_UIEventTypeMotion = 1
_UIEventTypeRemoteControl = 2
_UIEventTypePresses = 3
_UIEventTypePhysicalKeyboard = 4

_UIEventSubtypeNone = 0

# UIEventKeyCode

UIEventKeyCodeRight = 79
UIEventKeyCodeLeft = 80
UIEventKeyCodeDown = 81
UIEventKeyCodeUp = 82
UIEventKeyCodeEnter = 40
UIEventKeyCodeSpace = 44
UIEventKeyCodeBackspace = 42
UIEventKeyCodeEscape = 41
UIEventKeyCodeLeftSquareBracket = 47

_key_event_handlers = []


class KeyEventHandler(object):
    def __init__(self, key_code, modifier_flags, fn):
        self.key_code = key_code
        self.modifier_flags = modifier_flags
        self.fn = fn


def _blackmamba_handleKeyUIEvent(_self, _cmd, event):
    e = ObjCInstance(event)

#     debug('Down: {} Type: {} Subtype: {} Modifier flags: {} Keycode: {}'
#           .format(e._isKeyDown(), e.type(), e.subtype(), e._modifierFlags(), e._keyCode()))

    if e.type() == _UIEventTypePhysicalKeyboard and e.subtype() == _UIEventSubtypeNone and not e._isKeyDown():
        for h in _key_event_handlers:
            if h.key_code == e._keyCode() and h.modifier_flags == e._modifierFlags():
                h.fn()

    ObjCInstance(_self).originalhandleKeyUIEvent_(e)


@on_main_thread
def register_key_event_handler(key_code, func, *, modifier_flags=0):
    if not UIApplication.sharedApplication().respondsToSelector_(sel('originalhandleKeyUIEvent:')):
        swizzle('UIApplication', 'handleKeyUIEvent:', _blackmamba_handleKeyUIEvent)

    @system.catch_exceptions
    def invoke_func():
        func()

    handler = KeyEventHandler(key_code, modifier_flags, invoke_func)
    _key_event_handlers.append(handler)
    return handler


@on_main_thread
def unregister_key_event_handler(handler):
    try:
        _key_event_handlers.remove(handler)
    except ValueError:
        pass
