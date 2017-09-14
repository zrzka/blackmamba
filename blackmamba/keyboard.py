#!python3

import blackmamba.system as system

if system.IOS:
    from objc_util import ObjCClass
    UIKeyboardImpl = ObjCClass('UIKeyboardImpl')
else:
    UIKeyboardImpl = None


def is_in_hardware_keyboard_mode():
    if not UIKeyboardImpl:
        return False

    return UIKeyboardImpl.sharedInstance().isInHardwareKeyboardMode()
