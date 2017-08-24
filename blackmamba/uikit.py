#!python3

from objc_util import ObjCClass

UIKeyCommand = ObjCClass('UIKeyCommand')

# UIKeyModifierFlags

UIKeyModifierAlphaShift = 1 << 16  # CapsLock
UIKeyModifierShift = 1 << 17  # Shift
UIKeyModifierControl = 1 << 18  # Control
UIKeyModifierAlternate = 1 << 19  # Option
UIKeyModifierCommand = 1 << 20  # Command
UIKeyModifierNumericPad = 1 << 21  # Key is located on the numeric keypad

# UIEventType
#
# UIEventTypePhysicalKeyboard is not publicly defined in the UIKit. I just
# added it here so I can use it in events.

UIEventTypeTouches = 0
UIEventTypeMotion = 1
UIEventTypeRemoteControl = 2
UIEventTypePresses = 3
UIEventTypePhysicalKeyboard = 4

UIEventSubtypeNone = 0

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

# UITableViewCellStyle

UITableViewCellStyleDefault = 'default'
UITableViewCellStyleSubtitle = 'subtitle'
UITableViewCellStyleValue1 = 'value1'
UITableViewCellStyleValue2 = 'value2'
