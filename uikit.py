#!python3

from objc_util import ObjCClass

# UIKeyModifierFlags

UIKeyModifierAlphaShift = 1 << 16 # CapsLock
UIKeyModifierShift = 1 << 17 # Shift
UIKeyModifierControl = 1 << 18 # Control
UIKeyModifierAlternate = 1 << 19 # Option
UIKeyModifierCommand = 1 << 20 # Command
UIKeyModifierNumericPad = 1 << 21 # Key is located on the numeric keypad


# UIEventType

UIEventTypeTouches = 0
UIEventTypeMotion = 1
UIEventTypeRemoteControl = 2
UIEventTypePresses = 3
UIEventTypePhysicalKeyboard = 4

UIEventSubtypeNone = 0

UIKeyCommand = ObjCClass('UIKeyCommand')

