#!python3

from objc_util import on_main_thread, ObjCInstance, sel, UIApplication
from blackmamba.runtime import swizzle
from blackmamba.uikit import *

_key_event_handlers = []


class KeyEventHandler(object):
    def __init__(self, key_code, modifier_flags, fn):
        self.key_code = key_code
        self.modifier_flags = modifier_flags
        self.fn = fn


def _zrzka_handleKeyUIEvent(_self, _cmd, event):
    e = ObjCInstance(event)
    
#    print('Down: {} Type: {} Subtype: {} Modifier flags: {} Keycode: {}'
#        .format(e._isKeyDown(), e.type(), e.subtype(), e._modifierFlags(), e._keyCode()))
    
    if e.type() == UIEventTypePhysicalKeyboard and e.subtype() == 0 and not e._isKeyDown():
        for h in _key_event_handlers:
            if h.key_code == e._keyCode() and h.modifier_flags == e._modifierFlags():
                try:
                    h.fn()
                except Exception as ex:
                    print('Exception in key event handler {}'.format(h.fn))
                    print(ex)
    
    ObjCInstance(_self).originalhandleKeyUIEvent_(e)


@on_main_thread
def register_key_event_handler(key_code, fn, *, modifier_flags=0):
    if not UIApplication.sharedApplication().respondsToSelector_(sel('originalhandleKeyUIEvent:')):
        swizzle('UIApplication', 'handleKeyUIEvent:', _zrzka_handleKeyUIEvent)
    
    handler = KeyEventHandler(key_code, modifier_flags, fn)
    _key_event_handlers.append(handler)
    return handler
    
    
@on_main_thread
def unregister_key_event_handler(handler):
    try:
        _key_event_handlers.remove(handler)
    except ValueError:
        pass

