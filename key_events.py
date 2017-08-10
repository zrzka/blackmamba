#!python3

from runtime import swizzle
from objc_util import on_main_thread, ObjCInstance, sel, UIApplication
from uikit import *

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
                except:
                    pass
    
    ObjCInstance(_self).originalhandleKeyUIEvent_(e)


def _init_key_events_if_needed():
    if UIApplication.sharedApplication().respondsToSelector_(sel('originalhandleKeyUIEvent:')):
        return
        
    swizzle('UIApplication', 'handleKeyUIEvent:', _zrzka_handleKeyUIEvent)


@on_main_thread
def register_key_event_handler(key_code, fn, *, modifier_flags=0):
    _init_key_events_if_needed()
    
    handler = KeyEventHandler(key_code, modifier_flags, fn)
    _key_event_handlers.append(handler)
    return handler
    
    
@on_main_thread
def unregister_key_event_handler(handler):
    try:
        _key_event_handlers.remove(handler)
    except ValueError:
        pass

