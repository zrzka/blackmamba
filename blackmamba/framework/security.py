#!python3

"""Security.framework wrapper.

**Shared classes and constants**

* `ItemClass`
* `Accessibility`
* `AuthenticationPolicy`
* `AccessControl`
* `AuthenticationUI`

**Base classes for keychain items (passwords)**

These classes do provide shared implementation of methods like ``delete``, etc.

* `SecItem`
* `SecItemAttributes`

**Generic password specifics**

* `GenericPassword`
* `GenericPasswordAttributes`

**Internet password specifics**

* `InternetPassword`
* `InternetPasswordAttributes`
* `AuthenticationType`
* `Protocol`

**Errors**

Base class for all errors is `KeychainError`. If you'd like to catch all
security errors, just do::

    except KeychainError:
        pass

* `KeychainDuplicateItemError`
* `KeychainItemNotFoundError`
* `KeychainAuthFailedError`
* `KeychainUserCanceledError`
* `KeychainInteractionNotAllowedError`
* `KeychainParamError`
* `KeychainUnhandledError(KeychainError)`

**Pythonista compatibility**

Compatibility layer for Pythonista ``keychain`` module. Signature for all these
functions matches Pythonista ones.

These functions will not be enhanced to support ``prompt``, ``authentication_ui`` unless
Ole adds them to the Pythonista itself.

* `set_password`
* `get_password`
* `delete_password`
* `get_services`
* `reset_keychain`

Example how to use it as a ``keychain`` drop in replacement::

    import blackmamba.framework.security as keychain
    keychain.set_password('service', 'account', 'password')

**Low level wrappers**

All these wrappers operates with ``kSec*`` keys. These keys are not listed in the documentation
just to make it shorter.

You shouldn't use these low level wrappers unless you really need them. Stick with
`GenericPassword` or `InternetPassword`.

* `sec_item_add`
* `sec_item_copy_matching`, `sec_item_copy_matching_data`, `sec_item_copy_matching_attributes`
* `sec_item_update`
* `sec_item_delete`

**Examples**

Store generic password::

    gp = GenericPassword('service', 'account')
    gp.set_password('password')

Update generic password attributes::

    gp = GenericPassword('service', 'account')
    gp.comment = 'Great password'
    gp.description = 'Demo purposes, nothing elseeeee'
    gp.save()

Get generic password attributes::

    gp = GenericPassword('service', 'account')
    attrs = gp.get_attributes()
    print(attrs.creation_date)

Protect password with user presence::

    gp = GenericPassword('service', 'account')
    gp.access_control = AccessControl(
        Accessibility.WHEN_PASSCODE_SET_THIS_DEVICE_ONLY,
        AuthenticationPolicy.TOUCH_ID_ANY | AuthenticationPolicy.OR | AuthenticationPolicy.DEVICE_PASSCODE
    )
    gp.set_password('password')

Get protected password::

    gp = GenericPassword('service', 'account')
    try:
        password = gp.get_password(
            prompt='Your finger!'
        )
        print(password)
    except KeychainUserCanceledError:
        print('User did tap on Cancel, no password')
    except KeychainAuthFailedError:
        print('Authentication failed, no password')

Disable authentication UI for protected items::

    gp = GenericPassword('service', 'account')
    try:
        password = gp.get_password(
            prompt='Your finger!',
            authentication_ui=AuthenticationUI.FAIL
        )
        print(password)
    except KeychainInteractionNotAllowedError:
        print('Item is protected, authentication UI disabled, no password')

Skip protected items::

    gp = GenericPassword('service', 'account')
    try:
        password = gp.get_password(
            prompt='Your finger!',
            authentication_ui=AuthenticationUI.SKIP
        )
        print(password)
    except KeychainItemNotFoundError:
        print('Authentication UI disabled, protected items skipped, no password')

Query for generic passwords::

    try:
        for x in GenericPassword.query_items():
            print(f'{x.creation_date} {x.service} {x.account}')
    except KeychainItemNotFoundError:
        print('No generic password items')
    except KeychainUserCanceledError:
        print('Some items are protected, but user cancels authentication')
    except KeychainAuthFailedError:
        print('Some items are protected, but authentication failed')

Limit to specific service::

    GenericPassword.query_items(service='service')

Skip protected items:

    GenericPassword.query_items(authentication_ui=AuthenticationUI.SKIP)

Internet password::
    
    ip = InternetPassword('zrzka', server='https://github.com/',
                          protocol=Protocol.HTTPS, authentication_type=AuthenticationType.HTML_FORM)
    ip.set_password('password')    
    
Query internet passwords::
    
    for x in InternetPassword.query_items(server='https://github.com/'):
        print(f'{x.creation_date} {x.account} {x.protocol} {x.authentication_type}')

"""

from ctypes import c_int, c_void_p, POINTER, byref, c_ulong
from objc_util import (
    load_framework, c, ns, ObjCInstance, nsdata_to_bytes, NSString, NSData, NSNumber,
    ObjCClass, NSArray, NSDictionary
)
from enum import Enum, IntFlag
import datetime
import blackmamba.system as system
from typing import List, Union


#
# Core Foundation
#
# Memory management rules
# https://developer.apple.com/library/content/documentation/CoreFoundation/Conceptual/CFMemoryMgmt/CFMemoryMgmt.html
#
# Toll-free bridged types - we're not forced to play with CFDictionaryCreate - we can use ns(dict) -> NSDictionary directlyy
# https://developer.apple.com/library/content/documentation/CoreFoundation/Conceptual/CFDesignConcepts/Articles/tollFreeBridgedTypes.html
#

load_framework('Security')

NSDate = ObjCClass('NSDate')


def _from_nsstring(obj):
    return obj.UTF8String().decode()


def _from_nsnumber(obj):  # noqa: C901
    ctype = obj.objCType()
    if ctype == b'c':
        return obj.charValue()
    elif ctype == b's':
        return obj.shortValue()
    elif ctype == b'i':
        return obj.intValue()
    elif ctype == b'l':
        return obj.longValue()
    elif ctype == b'q':
        return obj.longLongValue()
    elif ctype == b'C':
        return obj.unsignedCharValue()
    elif ctype == b'S':
        return obj.unsignedShortValue()
    elif ctype == b'I':
        return obj.unsignedIntValue()
    elif ctype == b'L':
        return obj.unsignedLongValue()
    elif ctype == b'Q':
        return obj.unsignedLongLongValue()
    elif ctype == b'f':
        return obj.floatValue()
    elif ctype == b'd':
        return obj.doubleValue()
    elif ctype == b'B':
        return obj.boolValue()

    return obj


def _from_nsdata(obj):
    return nsdata_to_bytes(obj)


def _from_nsdate(obj):
    return datetime.datetime.fromtimestamp(obj.timeIntervalSince1970())


def _from_ns(obj):
    if obj.isKindOfClass_(NSString):
        return _from_nsstring(obj)
    elif obj.isKindOfClass_(NSNumber):
        return _from_nsnumber(obj)
    elif obj.isKindOfClass_(NSData):
        return _from_nsdata(obj)
    elif obj.isKindOfClass_(NSDate):
        return _from_nsdate(obj)
    elif obj.isKindOfClass_(NSArray):
        return [_from_ns(obj.objectAtIndex_(i) for i in range(obj.count()))]
    elif obj.isKindOfClass_(NSDictionary):
        return {_from_ns(k): _from_ns(obj.objectForKey_(k)) for k in obj.allKeys()}

    return obj


def _symbol_ptr(name):
    return c_void_p.in_dll(c, name)


def _str_symbol(name):
    # [TODO] Sphinx quick hack, remove
    if not system.IOS:
        return name

    return ObjCInstance(_symbol_ptr(name)).UTF8String().decode()


#
# kSec* constants
#
#


# https://developer.apple.com/documentation/security/keychain_services/keychain_items/item_class_keys_and_values?language=objc
kSecClass = _str_symbol('kSecClass')
kSecClassGenericPassword = _str_symbol('kSecClassGenericPassword')
kSecClassInternetPassword = _str_symbol('kSecClassInternetPassword')

# https://developer.apple.com/documentation/security/keychain_services/keychain_items/item_attribute_keys_and_values
# General Item Attribute Keys
kSecAttrAccessControl = _str_symbol('kSecAttrAccessControl')
kSecAttrAccessible = _str_symbol('kSecAttrAccessible')
kSecAttrAccessGroup = _str_symbol('kSecAttrAccessGroup')
kSecAttrSynchronizable = _str_symbol('kSecAttrSynchronizable')
kSecAttrCreationDate = _str_symbol('kSecAttrCreationDate')
kSecAttrModificationDate = _str_symbol('kSecAttrModificationDate')
kSecAttrDescription = _str_symbol('kSecAttrDescription')
kSecAttrComment = _str_symbol('kSecAttrComment')
kSecAttrCreator = _str_symbol('kSecAttrCreator')
kSecAttrType = _str_symbol('kSecAttrType')
kSecAttrLabel = _str_symbol('kSecAttrLabel')
kSecAttrIsInvisible = _str_symbol('kSecAttrIsInvisible')
kSecAttrIsNegative = _str_symbol('kSecAttrIsNegative')
kSecAttrSyncViewHint = _str_symbol('kSecAttrSyncViewHint')

# Password Attribute Keys (generic & internet password)
kSecAttrAccount = _str_symbol('kSecAttrAccount')

# Password Attribute Keys (generic password only)
kSecAttrService = _str_symbol('kSecAttrService')
kSecAttrGeneric = _str_symbol('kSecAttrGeneric')

# Password Attribute Keys (internet password only)
kSecAttrSecurityDomain = _str_symbol('kSecAttrSecurityDomain')
kSecAttrServer = _str_symbol('kSecAttrServer')
kSecAttrProtocol = _str_symbol('kSecAttrProtocol')
kSecAttrAuthenticationType = _str_symbol('kSecAttrAuthenticationType')
kSecAttrPort = _str_symbol('kSecAttrPort')
kSecAttrPath = _str_symbol('kSecAttrPath')

# kSecAttrProtocol values
kSecAttrProtocolFTP = _str_symbol('kSecAttrProtocolFTP')
kSecAttrProtocolFTPAccount = _str_symbol('kSecAttrProtocolFTPAccount')
kSecAttrProtocolHTTP = _str_symbol('kSecAttrProtocolHTTP')
kSecAttrProtocolIRC = _str_symbol('kSecAttrProtocolIRC')
kSecAttrProtocolNNTP = _str_symbol('kSecAttrProtocolNNTP')
kSecAttrProtocolPOP3 = _str_symbol('kSecAttrProtocolPOP3')
kSecAttrProtocolSMTP = _str_symbol('kSecAttrProtocolSMTP')
kSecAttrProtocolSOCKS = _str_symbol('kSecAttrProtocolSOCKS')
kSecAttrProtocolIMAP = _str_symbol('kSecAttrProtocolIMAP')
kSecAttrProtocolLDAP = _str_symbol('kSecAttrProtocolLDAP')
kSecAttrProtocolAppleTalk = _str_symbol('kSecAttrProtocolAppleTalk')
kSecAttrProtocolAFP = _str_symbol('kSecAttrProtocolAFP')
kSecAttrProtocolTelnet = _str_symbol('kSecAttrProtocolTelnet')
kSecAttrProtocolSSH = _str_symbol('kSecAttrProtocolSSH')
kSecAttrProtocolFTPS = _str_symbol('kSecAttrProtocolFTPS')
kSecAttrProtocolHTTPS = _str_symbol('kSecAttrProtocolHTTPS')
kSecAttrProtocolHTTPProxy = _str_symbol('kSecAttrProtocolHTTPProxy')
kSecAttrProtocolHTTPSProxy = _str_symbol('kSecAttrProtocolHTTPSProxy')
kSecAttrProtocolFTPProxy = _str_symbol('kSecAttrProtocolFTPProxy')
kSecAttrProtocolSMB = _str_symbol('kSecAttrProtocolSMB')
kSecAttrProtocolRTSP = _str_symbol('kSecAttrProtocolRTSP')
kSecAttrProtocolRTSPProxy = _str_symbol('kSecAttrProtocolRTSPProxy')
kSecAttrProtocolDAAP = _str_symbol('kSecAttrProtocolDAAP')
kSecAttrProtocolEPPC = _str_symbol('kSecAttrProtocolEPPC')
kSecAttrProtocolIPP = _str_symbol('kSecAttrProtocolIPP')
kSecAttrProtocolNNTPS = _str_symbol('kSecAttrProtocolNNTPS')
kSecAttrProtocolLDAPS = _str_symbol('kSecAttrProtocolLDAPS')
kSecAttrProtocolTelnetS = _str_symbol('kSecAttrProtocolTelnetS')
kSecAttrProtocolIMAPS = _str_symbol('kSecAttrProtocolIMAPS')
kSecAttrProtocolIRCS = _str_symbol('kSecAttrProtocolIRCS')
kSecAttrProtocolPOP3S = _str_symbol('kSecAttrProtocolPOP3S')

# kSecAttrAuthenticationType values
kSecAttrAuthenticationTypeNTLM = _str_symbol('kSecAttrAuthenticationTypeNTLM')
kSecAttrAuthenticationTypeMSN = _str_symbol('kSecAttrAuthenticationTypeMSN')
kSecAttrAuthenticationTypeDPA = _str_symbol('kSecAttrAuthenticationTypeDPA')
kSecAttrAuthenticationTypeRPA = _str_symbol('kSecAttrAuthenticationTypeRPA')
kSecAttrAuthenticationTypeHTTPBasic = _str_symbol('kSecAttrAuthenticationTypeHTTPBasic')
kSecAttrAuthenticationTypeHTTPDigest = _str_symbol('kSecAttrAuthenticationTypeHTTPDigest')
kSecAttrAuthenticationTypeHTMLForm = _str_symbol('kSecAttrAuthenticationTypeHTMLForm')
kSecAttrAuthenticationTypeDefault = _str_symbol('kSecAttrAuthenticationTypeDefault')

# https://developer.apple.com/documentation/security/keychain_services/keychain_items/item_return_result_keys?language=objc
kSecReturnData = _str_symbol('kSecReturnData')
kSecReturnAttributes = _str_symbol('kSecReturnAttributes')
kSecReturnRef = _str_symbol('kSecReturnRef')
kSecReturnPersistentRef = _str_symbol('kSecReturnPersistentRef')

# https://developer.apple.com/documentation/security/keychain_services/keychain_items/item_return_result_keys?language=objc
kSecValueData = _str_symbol('kSecValueData')
kSecValueRef = _str_symbol('kSecValueRef')
kSecValuePersistentRef = _str_symbol('kSecValuePersistentRef')

# https://developer.apple.com/documentation/security/keychain_services/keychain_items/search_attribute_keys_and_values?language=objc
kSecMatchLimit = _str_symbol('kSecMatchLimit')
kSecMatchLimitAll = _str_symbol('kSecMatchLimitAll')
kSecMatchLimitOne = _str_symbol('kSecMatchLimitOne')
kSecMatchCaseInsensitive = _str_symbol('kSecMatchCaseInsensitive')

# https://developer.apple.com/documentation/security/keychain_services/keychain_items/item_attribute_keys_and_values#1679100?language=objc
kSecAttrAccessibleAlways = _str_symbol('kSecAttrAccessibleAlways')
kSecAttrAccessibleAlwaysThisDeviceOnly = _str_symbol('kSecAttrAccessibleAlwaysThisDeviceOnly')
kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly = _str_symbol('kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly')
kSecAttrAccessibleAfterFirstUnlock = _str_symbol('kSecAttrAccessibleAfterFirstUnlock')
kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly = _str_symbol('kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly')
kSecAttrAccessibleWhenUnlocked = _str_symbol('kSecAttrAccessibleWhenUnlocked')
kSecAttrAccessibleWhenUnlockedThisDeviceOnly = _str_symbol('kSecAttrAccessibleWhenUnlockedThisDeviceOnly')

# https://developer.apple.com/documentation/security/secaccesscontrolcreateflags/ksecaccesscontroluserpresence
kSecAccessControlUserPresence = 1 << 0
kSecAccessControlTouchIDAny = 1 << 1
kSecAccessControlTouchIDCurrentSet = 1 << 3
kSecAccessControlDevicePasscode = 1 << 4
kSecAccessControlOr = 1 << 14
kSecAccessControlAnd = 1 << 15
kSecAccessControlPrivateKeyUsage = 1 << 30
kSecAccessControlApplicationPassword = 1 << 31

# https://developer.apple.com/documentation/security/ksecuseauthenticationuiallow?language=objc
kSecUseAuthenticationUI = _str_symbol('kSecUseAuthenticationUI')
kSecUseAuthenticationUIAllow = _str_symbol('kSecUseAuthenticationUIAllow')
kSecUseAuthenticationUIFail = _str_symbol('kSecUseAuthenticationUIFail')
kSecUseAuthenticationUISkip = _str_symbol('kSecUseAuthenticationUISkip')

kSecUseOperationPrompt = _str_symbol('kSecUseOperationPrompt')

#
# Security framework functions
#

CFTypeRef = c_void_p
CFDictionaryRef = c_void_p
SecAccessControlRef = c_void_p
CFErrorRef = c_void_p
CFAllocatorRef = c_void_p

# void CFRelease(CFTypeRef cf)
# https://developer.apple.com/documentation/corefoundation/1521153-cfrelease
CFRelease = c.CFRelease
CFRelease.restype = None
CFRelease.argtypes = [CFTypeRef]

# OSStatus SecItemAdd(CFDictionaryRef attributes, CFTypeRef  _Nullable *result);
# https://developer.apple.com/documentation/security/1401659-secitemadd?language=objc
SecItemAdd = c.SecItemAdd
SecItemAdd.restype = c_int
SecItemAdd.argtypes = [CFDictionaryRef, POINTER(CFTypeRef)]

# OSStatus SecItemUpdate(CFDictionaryRef query, CFDictionaryRef attributesToUpdate);
# https://developer.apple.com/documentation/security/1393617-secitemupdate?language=objc
SecItemUpdate = c.SecItemUpdate
SecItemUpdate.restype = c_int
SecItemUpdate.argtypes = [CFDictionaryRef, CFDictionaryRef]

# OSStatus SecItemCopyMatching(CFDictionaryRef query, CFTypeRef  _Nullable *result);
# https://developer.apple.com/documentation/security/1398306-secitemcopymatching?language=objc
SecItemCopyMatching = c.SecItemCopyMatching
SecItemCopyMatching.restype = c_int
SecItemCopyMatching.argtypes = [CFDictionaryRef, POINTER(CFTypeRef)]

# OSStatus SecItemDelete(CFDictionaryRef query);
# https://developer.apple.com/documentation/security/1395547-secitemdelete?language=objc
SecItemDelete = c.SecItemDelete
SecItemDelete.restype = c_int
SecItemDelete.argtypes = [CFDictionaryRef]

# SecAccessControlRef SecAccessControlCreateWithFlags(CFAllocatorRef allocator, CFTypeRef protection,
#                                                     SecAccessControlCreateFlags flags, CFErrorRef  _Nullable *error);
# https://developer.apple.com/documentation/security/1394452-secaccesscontrolcreatewithflags?language=objc
SecAccessControlCreateWithFlags = c.SecAccessControlCreateWithFlags
SecAccessControlCreateWithFlags.restype = SecAccessControlRef
SecAccessControlCreateWithFlags.argtypes = [CFAllocatorRef, CFTypeRef, c_ulong, POINTER(CFErrorRef)]

#
# Keychain errors
#

_status_error_classes = {}


def register_status_error(status=None):
    def decorator(cls):
        _status_error_classes[status] = cls
        return cls

    return decorator


class KeychainError(Exception):
    """Base class for all security module errors.

    Args:
        *args: Passed to super class
        status (int, optional): `OSStatus` error if applicable or `None`

    Attributes:
        status (int, optional): `OSStatus` error code or `None`
    """

    def __init__(self, *args, status: int = None):
        super().__init__(*args)
        self.status = status


@register_status_error(-25299)
class KeychainDuplicateItemError(KeychainError):
    """Keychain item already exists."""


@register_status_error(-25300)
class KeychainItemNotFoundError(KeychainError):
    """Keychain item does not exist."""


@register_status_error(-25293)
class KeychainAuthFailedError(KeychainError):
    """Authentication failed."""


@register_status_error(-128)
class KeychainUserCanceledError(KeychainError):
    """User cancels authentication."""


@register_status_error(-25308)
class KeychainInteractionNotAllowedError(KeychainError):
    """User interaction is not allowed."""


@register_status_error(-50)
class KeychainParamError(KeychainError):
    """Invalid parameters."""


@register_status_error()
class KeychainUnhandledError(KeychainError):
    """Generic keychain error."""


def _error_class_with_status(status):
    return _status_error_classes.get(status, _status_error_classes[None])


def _raise_status(status, *args):
    if status:
        raise _error_class_with_status(status)(*args, status=status)


def sec_item_add(attributes: dict) -> None:
    """SecItemAdd wrapper.

    Args:
        attributes: Keychain item attributes.

    Raises:
        KeychainDuplicateItemError: Keychain item already exists.
        KeychainParamError: Invalid combination of parameters.
        KeychainUnhandledError: Any other Security framework error, check `status` property.
    """

    _raise_status(
        SecItemAdd(ns(attributes), None),
        'Failed to add keychain item'
    )


def sec_item_update(query_attributes: dict, attributes_to_update: dict) -> None:
    """SecItemUpdate wrapper.

    Args:
        query_attributes: Item query attributes.
        attributes_to_update: Attributes that should be updated.

    Raises:
        KeychainItemNotFoundError: Keychain item not found.
        KeychainAuthFailedError: Authentication failed.
        KeychainUserCanceledError: User cancels authentication.
        KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
        KeychainParamError: Invalid parameters combination.
        KeychainUnhandledError: Any other Security framework error, check `status` property.
    """

    _raise_status(
        SecItemUpdate(ns(query_attributes), ns(attributes_to_update)),
        'Failed to update keychain item'
    )


def sec_item_copy_matching(query_attributes: dict) -> ObjCInstance:
    """SecItemCopyMatching wrapper.

    Args:
        query_attributes: Keychain item attributes.

    Returns:
        `ObjCInstance` which can be hold `NSDictionary` or `NSData`.

    Raises:
        KeychainItemNotFoundError: Keychain item not found.
        KeychainAuthFailedError: Authentication failed.
        KeychainUserCanceledError: User cancels authentication.
        KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
        KeychainParamError: Invalid parameters combination.
        KeychainUnhandledError: Any other Security framework error, check `status` property.
    """
    ptr = CFTypeRef()
    _raise_status(
        SecItemCopyMatching(ns(query_attributes), byref(ptr)),
        'Failed to get keychain item'
    )

    assert (ptr.value is not None)

    result = ObjCInstance(ptr)
    CFRelease(ptr)
    return result


def sec_item_copy_matching_data(query_attributes: dict) -> bytes:
    """SecItemCopy wrapper.

    Calls `sec_item_copy_matching` and forces data retrieval.

    Args:
        query_attributes: Keychain item attributes.

    Raises:
        KeychainItemNotFoundError: Keychain item not found.
        KeychainAuthFailedError: Authentication failed.
        KeychainUserCanceledError: User cancels authentication.
        KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
        KeychainParamError: Invalid parameters combination.
        KeychainUnhandledError: Any other Security framework error, check `status` property.
    """

    query = dict(query_attributes)
    query[kSecReturnAttributes] = False
    query[kSecReturnData] = True

    return _from_ns(sec_item_copy_matching(query))


def sec_item_copy_matching_attributes(query_attributes: dict) -> dict:
    """SecItemCopy wrapper.

    Calls `sec_item_copy_matching` and forces attributes retrieval.

    Args:
        query_attributes: Keychain item attributes.

    Raises:
        KeychainItemNotFoundError: Keychain item not found.
        KeychainAuthFailedError: Authentication failed.
        KeychainUserCanceledError: User cancels authentication.
        KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
        KeychainParamError: Invalid parameters combination.
        KeychainUnhandledError: Any other Security framework error, check `status` property.
    """

    query = dict(query_attributes)
    query[kSecReturnAttributes] = True
    query[kSecReturnData] = False

    return _from_ns(sec_item_copy_matching(query))


def sec_item_delete(query_attributes: dict) -> None:
    """SecItemDelete wrapper.

    Args:
        query_attributes: Keychain item attributes

    Raises:
        KeychainItemNotFoundError: Keychain item not found.
        KeychainParamError: Invalid parameters combination.
        KeychainUnhandledError: Any other Security framework error, check `status` property.
    """

    _raise_status(
        SecItemDelete(ns(query_attributes)),
        'Failed to delete keychain item'
    )


class ItemClass(str, Enum):
    """Keychain item class.

    * `GENERIC_PASSWORD` - The value that indicates a generic password item.

    * `INTERNET_PASSWORD` - The value that indicates an Internet password item.
    """

    GENERIC_PASSWORD = kSecClassGenericPassword
    INTERNET_PASSWORD = kSecClassInternetPassword


class AuthenticationPolicy(IntFlag):
    """Protection class to be used for the item.

    * `USER_PRESENCE` - Constraint to access an item with either Touch ID or passcode.

      Touch ID does not have to be available or enrolled. The item is still
      accessible by Touch ID even if fingers are added or removed.

    * `TOUCH_ID_ANY` - Constraint to access an item with Touch ID for any enrolled
      fingers.

      Touch ID must be available and enrolled with at least one finger. The item is
      still accessible by Touch ID if fingers are added or removed.

    * `TOUCH_ID_CURRENT_SET` - Constraint to access an item with Touch ID for currently
      enrolled fingers.

      Touch ID must be available and enrolled with at least one finger. The item is
      invalidated if fingers are added or removed.

    * `DEVICE_PASSCODE` - Constraint to access an item with a passcode.

    * `OR` - Logical disjunction operation, such that when specifying more than one
      constraint, at least one must be satisfied.

    * `AND` - Logical conjunction operation, such that when specifying more than one
      constraint, all of them must be satisfied.

    * `APPLICATION_PASSWORD` - Option to use an application-provided password for data
      encryption key generation.

      This may be specified in addition to any constraints.
    """

    USER_PRESENCE = kSecAccessControlUserPresence
    TOUCH_ID_ANY = kSecAccessControlTouchIDAny
    TOUCH_ID_CURRENT_SET = kSecAccessControlTouchIDCurrentSet
    DEVICE_PASSCODE = kSecAccessControlDevicePasscode
    OR = kSecAccessControlOr
    AND = kSecAccessControlAnd
    APPLICATION_PASSWORD = kSecAccessControlApplicationPassword


class Accessibility(str, Enum):
    """Indicates when a keychain item is accessible.

    You should choose the most restrictive option that meets your app’s needs so
    that the system can protect that item to the greatest extent possible.

    Default value is `WHEN_UNLOCKED`.

    * `ALWAYS` - The data in the keychain item can always be accessed regardless
      of whether the device is locked.

      This is not recommended for application use. Items with this attribute
      migrate to a new device when using encrypted backups.

    * `ALWAYS_THIS_DEVICE_ONLY` - The data in the keychain item can always be
      accessed regardless of whether the device is locked.

      This is not recommended for application use. Items with this attribute do
      not migrate to a new device. Thus, after restoring from a backup of a
      different device, these items will not be present.

    * `WHEN_PASSCODE_SET_THIS_DEVICE_ONLY` - The data in the keychain can only be
      accessed when the device is unlocked.

      Only available if a passcode is set on the device.

      This is recommended for items that only need to be accessible while the
      application is in the foreground. Items with this attribute never migrate
      to a new device. After a backup is restored to a new device, these items
      are missing. No items can be stored in this class on devices without a
      passcode. Disabling the device passcode causes all items in this class to
      be deleted.

    * `AFTER_FIRST_UNLOCK` - The data in the keychain item cannot be accessed
      after a restart until the device has been unlocked once by the user.

      After the first unlock, the data remains accessible until the next restart.
      This is recommended for items that need to be accessed by background
      applications. Items with this attribute migrate to a new device when using
      encrypted backups.

    * `AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY` - The data in the keychain item cannot
      be accessed after a restart until the device has been unlocked once by the
      user.

      After the first unlock, the data remains accessible until the next restart.
      This is recommended for items that need to be accessed by background
      applications. Items with this attribute do not migrate to a new device.
      Thus, after restoring from a backup of a different device, these items will
      not be present.

    * `WHEN_UNLOCKED` - The data in the keychain item can be accessed only while
      the device is unlocked by the user.

      This is recommended for items that need to be accessible only while the
      application is in the foreground. Items with this attribute migrate to a new
      device when using encrypted backups.

      This is the default value for keychain items added without explicitly
      setting an accessibility constant.

    * `WHEN_UNLOCKED_THIS_DEVICE_ONLY` - The data in the keychain item can be
      accessed only while the device is unlocked by the user.

      This is recommended for items that need to be accessible only while the
      application is in the foreground. Items with this attribute do not migrate
      to a new device. Thus, after restoring from a backup of a different device,
      these items will not be present.
    """

    ALWAYS = kSecAttrAccessibleAlways
    ALWAYS_THIS_DEVICE_ONLY = kSecAttrAccessibleAlwaysThisDeviceOnly
    WHEN_PASSCODE_SET_THIS_DEVICE_ONLY = kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly
    AFTER_FIRST_UNLOCK = kSecAttrAccessibleAfterFirstUnlock
    AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
    WHEN_UNLOCKED = kSecAttrAccessibleWhenUnlocked
    WHEN_UNLOCKED_THIS_DEVICE_ONLY = kSecAttrAccessibleWhenUnlockedThisDeviceOnly


class Protocol(str, Enum):
    """Indicates the item's protocol.

    Items of class `ItemClass.INTERNET_PASSWORD` have this attribute.

    * `FTP` - FTP protocol.
    * `FTP_ACCOUNT` - A client side FTP account.
    * `HTTP` - HTTP protocol.
    * `IRC` - IRC protocol.
    * `NNTP` - NNTP protocol.
    * `POP3` - POP3 protocol.
    * `SMTP` - SMTP protocol.
    * `SOCKS` - SOCKS protocol.
    * `IMAP` - IMAP protocol.
    * `LDAP` - LDAP protocol.
    * `APPLETALK` - AFP over AppleTalk.
    * `AFTP` - AFP over TCP.
    * `TELNET` - Telnet protocol.
    * `SSH` - SSH protocol.
    * `FTPS` - FTP over TLS/SSL.
    * `HTTPS` - HTTP over TLS/SSL.
    * `HTTP_PROXY` - HTTP proxy.
    * `HTTPS_PROXY` - HTTPS proxy.
    * `FTP_PROXY` - FTP proxy.
    * `SMB` - SMB protocol.
    * `RTSP` - RTSP protocol.
    * `RTSP_PROXY` - RTSP proxy.
    * `DAAP` - DAAP protocol.
    * `EPPC` - Remote Apple Events.
    * `IPP` - IPP protocol.
    * `NNTPS` - NNTP over TLS/SSL.
    * `LDAPS` - LDAP over TLS/SSL.
    * `TELNETS` - Telnet over TLS/SSL.
    * `IMAPS` - IMAP over TLS/SSL.
    * `IRCS` - IRC over TLS/SSL.
    * `POP3S` - POP3 over TLS/SSL.
    """

    FTP = kSecAttrProtocolFTP
    FTP_ACCOUNT = kSecAttrProtocolFTPAccount
    HTTP = kSecAttrProtocolHTTP
    IRC = kSecAttrProtocolIRC
    NNTP = kSecAttrProtocolNNTP
    POP3 = kSecAttrProtocolPOP3
    SMTP = kSecAttrProtocolSMTP
    SOCKS = kSecAttrProtocolSOCKS
    IMAP = kSecAttrProtocolIMAP
    LDAP = kSecAttrProtocolLDAP
    APPLETALK = kSecAttrProtocolAppleTalk
    AFTP = kSecAttrProtocolAFP
    TELNET = kSecAttrProtocolTelnet
    SSH = kSecAttrProtocolSSH
    FTPS = kSecAttrProtocolFTPS
    HTTPS = kSecAttrProtocolHTTPS
    HTTP_PROXY = kSecAttrProtocolHTTPProxy
    HTTPS_PROXY = kSecAttrProtocolHTTPSProxy
    FTP_PROXY = kSecAttrProtocolFTPProxy
    SMB = kSecAttrProtocolSMB
    RTSP = kSecAttrProtocolRTSP
    RTSP_PROXY = kSecAttrProtocolRTSPProxy
    DAAP = kSecAttrProtocolDAAP
    EPPC = kSecAttrProtocolEPPC
    IPP = kSecAttrProtocolIPP
    NNTPS = kSecAttrProtocolNNTPS
    LDAPS = kSecAttrProtocolLDAPS
    TELNETS = kSecAttrProtocolTelnetS
    IMAPS = kSecAttrProtocolIMAPS
    IRCS = kSecAttrProtocolIRCS
    POP3S = kSecAttrProtocolPOP3S


class AuthenticationType(str, Enum):
    """Indicates the item's authentication scheme.

    * `NTLM` - Windows NT LAN Manager authentication.
    * `MSN` - Microsoft Network default authentication.
    * `DPA` - Distributed Password authentication.
    * `RPA` - Remote Password authentication.
    * `HTTP_BASIC` - HTTP Basic authentication.
    * `HTTP_DIGEST` - HTTP Digest Access authentication.
    * `HTML_FORM` - HTML form based authentication.
    * `DEFAULT` - The default authentication type.
    """

    NTLM = kSecAttrAuthenticationTypeNTLM
    MSN = kSecAttrAuthenticationTypeMSN
    DPA = kSecAttrAuthenticationTypeDPA
    RPA = kSecAttrAuthenticationTypeRPA
    HTTP_BASIC = kSecAttrAuthenticationTypeHTTPBasic
    HTTP_DIGEST = kSecAttrAuthenticationTypeHTTPDigest
    HTML_FORM = kSecAttrAuthenticationTypeHTMLForm
    DEFAULT = kSecAttrAuthenticationTypeDefault


class AuthenticationUI(str, Enum):
    """Indicates whether the user may be prompted for authentication.

    A default value of `ALLOW` is assumed when this key is not present.

    * `ALLOW` - A value that indicates user authentication is allowed.

      The user may be prompted for authentication. This is the default value.

    * `FAIL` - A value that indicates user authentication is disallowed.

      When you specify this value, if user authentication is needed, the
      `KeychainInteractionNotAllowedError` is raised.

    * `SKIP` - A value that indicates items requiring user authentication should
      be skipped.

      Silently skip any items that require user authentication.
    """

    ALLOW = kSecUseAuthenticationUIAllow
    FAIL = kSecUseAuthenticationUIFail
    SKIP = kSecUseAuthenticationUISkip


class AccessControl:
    """Allows you to combine accessibility and authentication policy.

    Args:
        protection (`Accessibility`): Keychain item protection
        flags (`AuthenticationPolicy`): Authentication policy
    """

    def __init__(self, protection: Accessibility, flags: AuthenticationPolicy):
        self._protection = protection
        self._flags = flags
        self._sac = None

    @property
    def protection(self) -> Accessibility:
        """Keychain item protection."""
        return self._protection

    @property
    def flags(self) -> AuthenticationPolicy:
        """Authentication policy flags."""
        return self._flags

    @property
    def value(self) -> ObjCInstance:
        """`SecAccessControl` object wrapped in `ObjCInstance`.

        Raises:
            KeychainError: Failed to create `SecAccessControl` object.
        """
        if not self._sac:
            sac = SecAccessControlCreateWithFlags(None, ns(self._protection.value), self._flags, None)

            if sac is None:
                raise KeychainError('Failed to create SecAccessControl object')

            self._sac = ObjCInstance(sac)
            CFRelease(sac)

        return self._sac


class SecItem:
    """Base class for all keychain items.

    Args:
        **kwargs: Keyword arguments where keys are matching attribute names and types.

    Attributes:
        accessibility (`Accessibility`): Indicates when a keychain item is accessible.
        access_control (`AccessControl`): Indicates access control settings for the item.
        description (str): Item description
        label (str): Item label
        comment (str): Item comment
        is_invisible (bool): Indicates the item's visibility.
        is_negative (bool): Indicates whether the item has a valid password.
    """

    _ITEM_CLASS = None

    def __init__(self, **kwargs):
        self.accessibility = kwargs.get('accessibility', None)
        self.access_control = kwargs.get('access_control', None)
        self.description = kwargs.get('description', None)
        self.label = kwargs.get('label', None)
        self.comment = kwargs.get('comment', None)
        self.is_invisible = kwargs.get('is_invisible', None)
        self.is_negative = kwargs.get('is_negative', None)

    @property
    def item_class(self) -> ItemClass:
        """`ItemClass`: Keychain item class."""
        return self._ITEM_CLASS

    def _query_attributes(self) -> dict:
        return {
            kSecClass: self.item_class
        }

    def _item_attributes(self) -> dict:
        attrs = {}

        if self.accessibility is not None:
            attrs[kSecAttrAccessible] = self.accessibility.value

        if self.access_control:
            attrs[kSecAttrAccessControl] = self.access_control.value

        if self.description:
            attrs[kSecAttrDescription] = self.description

        if self.label:
            attrs[kSecAttrLabel] = self.label

        if self.comment:
            attrs[kSecAttrComment] = self.comment

        if self.is_invisible:
            attrs[kSecAttrIsInvisible] = self.is_invisible

        if self.is_negative:
            attrs[kSecAttrIsNegative] = self.is_negative

        return attrs

    def _get_attributes(self, *, prompt: str = None,
                        authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> dict:
        query = self._query_attributes()
        query[kSecReturnAttributes] = True
        query[kSecReturnData] = False
        query[kSecMatchLimit] = kSecMatchLimitOne
        query[kSecUseAuthenticationUI] = authentication_ui

        if prompt:
            query[kSecUseOperationPrompt] = prompt

        return sec_item_copy_matching_attributes(query)

    def get_data(self, *, prompt: str = None, authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> bytes:
        """Get keychain item data.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """

        query = self._query_attributes()
        query[kSecReturnAttributes] = False
        query[kSecReturnData] = True
        query[kSecMatchLimit] = kSecMatchLimitOne
        query[kSecUseAuthenticationUI] = authentication_ui

        if prompt:
            query[kSecUseOperationPrompt] = prompt

        return sec_item_copy_matching_data(query)

    def delete(self):
        """Delete keychain item.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """
        sec_item_delete(self._query_attributes())

    def add(self, *, data: bytes = None, prompt: str = None,
            authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW):
        """Add item to the keychain.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            data (bytes, optional): Item data.
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Raises:
            KeychainDuplicateItemError: Keychain item already exists.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """
        attrs = self._query_attributes()
        attrs.update(self._item_attributes())
        attrs[kSecUseAuthenticationUI] = authentication_ui

        if data:
            attrs[kSecValueData] = data

        if prompt:
            attrs[kSecUseOperationPrompt] = prompt

        sec_item_add(attrs)

    def update(self, *, data: bytes = None, prompt: str = None,
               authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW):
        """Update keychain item.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            data (bytes, optional): Item data.
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """

        query = self._query_attributes()
        attrs = self._item_attributes()

        query[kSecUseAuthenticationUI] = authentication_ui

        if data:
            attrs[kSecValueData] = data

        if prompt:
            query[kSecUseOperationPrompt] = prompt

        sec_item_update(query, attrs)

    def save(self, *, data: bytes = None, prompt: str = None,
             authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW):
        """Save keychain item.

        Convenience method wrapping `add` and `update` methods. Use this method
        if you'd like to store keychain item and you don't care if it exists or
        not. It's handled automatically for you.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            data (bytes, optional): Item data.
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """

        try:
            self.add(data=data, prompt=prompt, authentication_ui=authentication_ui)
        except KeychainDuplicateItemError:
            self.update(data=data, prompt=prompt, authentication_ui=authentication_ui)

    @classmethod
    def _query_items(cls, attributes=None, *, prompt: str = None,
                     authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW):
        query = {
            kSecClass: cls._ITEM_CLASS,
            kSecReturnData: False,
            kSecReturnAttributes: True,
            kSecMatchLimit: kSecMatchLimitAll,
            kSecUseAuthenticationUI: authentication_ui
        }
        if prompt:
            query[kSecUseOperationPrompt] = prompt

        if attributes:
            query.update(attributes)

        result = sec_item_copy_matching(query)
        return [
            _from_ns(result.objectAtIndex_(i))
            for i in range(result.count())
        ]


class SecItemAttributes:
    """Base class for all keychain item attributes.

    .. note:: Do not instantiate this class on your own. You have
        to use `SecItem` subclass `get_attributes` instance method
        or `query_items` class method.

    Attributes:
        modification_date (datetime.datetime): Modification date.
        creation_date (datetime.datetime): Creation date.
        description (str): Item description.
        label (str): Item label.
        comment (str): Item comment.
        is_invisible (bool): Indicates the item's visibility.
        is_negative (bool): Indicates whether the item has a valid password.
    """

    def __init__(self, attrs):
        self.modification_date = attrs.get(kSecAttrModificationDate, None)
        self.creation_date = attrs.get(kSecAttrCreationDate, None)
        self.description = attrs.get(kSecAttrDescription, None)
        self.label = attrs.get(kSecAttrLabel, None)
        self.comment = attrs.get(kSecAttrComment, None)
        self.is_invisible = bool(attrs.get(kSecAttrIsInvisible, False))
        self.is_negative = bool(attrs.get(kSecAttrIsNegative, False))

        self.accessibility = Accessibility(attrs[kSecAttrAccessible]) if kSecAttrAccessible in attrs else None


class GenericPasswordAttributes(SecItemAttributes):
    """Generic password attributes.

    .. note:: Do not instantiate this class on your own. You have
        to use `GenericPassword.get_attributes` or
        `GenericPassword.query_items`.

    See also:
        `SecItemAttributes` for inherited attributes.

    Attributes:
        item_class (`ItemClass`): Always `ItemClass.GENERIC_PASSWORD`.
        service (str): Service.
        account (str): Account.
        generic (bytes): Custom data (not password).
    """

    def __init__(self, attrs):
        super().__init__(attrs)
        self.item_class = ItemClass.GENERIC_PASSWORD
        self.service = attrs.get(kSecAttrService, None)
        self.account = attrs.get(kSecAttrAccount, None)
        self.generic = attrs.get(kSecAttrGeneric, None)


class GenericPassword(SecItem):
    """Generic password wrapper.

    Args:
        service (str): Service.
        account (str): Account.

    Attributes:
        service (str): Service.
        account (str): Account.
        generic (bytes): Custom data (not password).
    """
    _ITEM_CLASS = ItemClass.GENERIC_PASSWORD

    def __init__(self, service: str, account: str):
        super().__init__()
        self._service = service
        self._account = account
        self.generic = None

    @property
    def service(self) -> str:
        return self._service

    @property
    def account(self):
        return self._account

    def _query_attributes(self):
        query = super()._query_attributes()
        query[kSecAttrService] = self.service
        query[kSecAttrAccount] = self.account
        return query

    def _item_attributes(self):
        attrs = super()._item_attributes()
        attrs[kSecAttrService] = self._service
        attrs[kSecAttrAccount] = self._account

        if self.generic:
            attrs[kSecAttrGeneric] = self.generic

        return attrs

    def get_attributes(self, *, prompt: str = None,
                       authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> GenericPasswordAttributes:
        """Fetch item attributes.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Returns:
            `GenericPasswordAttributes`: Attributes.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """
        return GenericPasswordAttributes(self._get_attributes(prompt=prompt, authentication_ui=authentication_ui))

    def get_password(self, *, prompt: str = None, authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> str:
        """Fetch item password.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Returns:
            str: Password.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """
        return self.get_data(prompt=prompt, authentication_ui=authentication_ui).decode()

    def set_password(self, password: str, *, prompt: str = None,
                     authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW):
        """Set item password.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            password (str): Password to set.
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """
        self.save(data=password.encode(), prompt=prompt, authentication_ui=authentication_ui)

    @classmethod
    def query_items(cls, service: str = None, *, prompt: str = None,
                    authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> List[GenericPasswordAttributes]:
        """Search for generic password items.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            service (str, optional): Limit search to specific service.
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Returns:
            List[GenericPasswordAttributes]: List of attributes.

        Raises:
            KeychainItemNotFoundError: Keychain items not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """
        attrs = {}
        if service:
            attrs[kSecAttrService] = service

        return [
            GenericPasswordAttributes(x)
            for x in cls._query_items(attrs, prompt=prompt, authentication_ui=authentication_ui)
        ]


class InternetPasswordAttributes(SecItemAttributes):
    """Internet password attributes.

    .. note:: Do not instantiate this class on your own. You have
        to use `InternetPassword.get_attributes` or
        `InternetPassword.query_items`.

    See also:
        `SecItemAttributes` for inherited attributes.

    Attributes:
        item_class (`ItemClass`): Always `ItemClass.INTERNET_PASSWORD`.
        account (str): Account.
        security_domain (str): Security domain.
        server (str): Server.
        protocol (`Protocol`): Protocol.
        authentication_type (`AuthenticationType`): Authentication type.
        port (int): Port.
    """

    def __init__(self, attrs):
        super().__init__(attrs)
        self.item_class = ItemClass.INTERNET_PASSWORD
        self.account = attrs.get(kSecAttrAccount, None)
        self.security_domain = attrs.get(kSecAttrSecurityDomain, None)
        self.server = attrs.get(kSecAttrServer, None)
        self.protocol = Protocol(attrs[kSecAttrProtocol]) if kSecAttrProtocol in attrs else None
        self.authentication_type = AuthenticationType(attrs[kSecAttrAuthenticationType]) \
            if kSecAttrAuthenticationType in attrs else None
        self.port = attrs.get(kSecAttrPort, None)


class InternetPassword(SecItem):
    """Internet password wrapper.

    Args:
        account (str): Account.
        security_domain (str): Security domain.
        server (str): Server.
        protocol (`Protocol`): Protocol.
        authentication_type (`AuthenticationType`): Authentication type.
        port (int): Port.

    Attributes:
        account (str): Account.
        security_domain (str): Security domain.
        server (str): Server.
        protocol (`Protocol`): Protocol.
        authentication_type (`AuthenticationType`): Authentication type.
        port (int): Port.
    """

    _ITEM_CLASS = ItemClass.INTERNET_PASSWORD

    def __init__(self, account: str,
                 security_domain: str = None,
                 server: str = None,
                 protocol: Protocol = None,
                 authentication_type: AuthenticationType = None,
                 port: int = None):
        super().__init__()
        self.account = account
        self.security_domain = security_domain
        self.server = server
        self.protocol = protocol
        self.authentication_type = authentication_type
        self.port = port

    def _query_attributes(self):
        query = super()._query_attributes()

        if self.account:
            query[kSecAttrAccount] = self.account

        if self.security_domain:
            query[kSecAttrSecurityDomain] = self.security_domain

        if self.server:
            query[kSecAttrServer] = self.server

        if self.protocol:
            query[kSecAttrProtocol] = self.protocol

        if self.authentication_type:
            query[kSecAttrAuthenticationType] = self.authentication_type

        if self.port is not None:
            query[kSecAttrPort] = self.port

        return query

    def _item_attributes(self):
        attrs = super()._item_attributes()

        if self.account:
            attrs[kSecAttrAccount] = self.account

        if self.security_domain:
            attrs[kSecAttrSecurityDomain] = self.security_domain

        if self.server:
            attrs[kSecAttrServer] = self.server

        if self.protocol:
            attrs[kSecAttrProtocol] = self.protocol

        if self.authentication_type:
            attrs[kSecAttrAuthenticationType] = self.authentication_type

        if self.port is not None:
            attrs[kSecAttrPort] = self.port

        return attrs

    def get_attributes(self, *, prompt: str = None,
                       authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> InternetPasswordAttributes:
        """Fetch item attributes.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Returns:
            `InternetPasswordAttributes`: Attributes.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """

        return InternetPasswordAttributes(self._get_attributes(prompt=prompt, authentication_ui=authentication_ui))

    def get_password(self, *, prompt: str = None, authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> str:
        """Fetch item password.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Returns:
            str: Password.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """

        return self.get_data(prompt=prompt, authentication_ui=authentication_ui).decode()

    def set_password(self, password, *, prompt: str = None,
                     authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW):
        """Set item password.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            password (str): Password to set.
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Raises:
            KeychainItemNotFoundError: Keychain item not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """

        self.save(data=password.encode(), prompt=prompt, authentication_ui=authentication_ui)

    @classmethod
    def query_items(cls, account: str = None, security_domain: str = None, server: str = None,
                    protocol: Protocol = None, authentication_type: AuthenticationType = None, port: int = None,
                    *, prompt: str = None,
                    authentication_ui: AuthenticationUI = AuthenticationUI.ALLOW) -> List[InternetPasswordAttributes]:
        """Search for internet password items.

        .. warning:: Never call on the main thread. UI can be locked up if the item is protected.

        Args:
            account (str): Account.
            security_domain (str): Security domain.
            server (str): Server.
            protocol (`Protocol`): Protocol.
            authentication_type (`AuthenticationType`): Authentication type.
            port (int): Port.
            prompt (str, optional): Authentication prompt.
            authentication_ui (`AuthenticationUI`): Indicates whether the user may be prompted for authentication.

        Returns:
            List[InternetPasswordAttributes]: List of attributes.

        Raises:
            KeychainItemNotFoundError: Keychain items not found.
            KeychainAuthFailedError: Authentication failed.
            KeychainUserCanceledError: User cancels authentication.
            KeychainInteractionNotAllowedError: Keychain item is protected and `AuthenticationUI` is set to `.FAIL`.
            KeychainParamError: Invalid parameters combination.
            KeychainUnhandledError: Any other Security framework error, check `status` property.
        """

        attrs = {}
        if account:
            attrs[kSecAttrAccount] = account

        if security_domain:
            attrs[kSecAttrSecurityDomain] = security_domain

        if server:
            attrs[kSecAttrServer] = server

        if protocol is not None:
            attrs[kSecAttrProtocol] = protocol

        if authentication_type:
            attrs[kSecAttrAuthenticationType] = authentication_type

        if port is not None:
            attrs[kSecAttrPort] = port

        return [
            InternetPasswordAttributes(x)
            for x in cls._query_items(attrs, prompt=prompt, authentication_ui=authentication_ui)
        ]


def delete_password(service, account):
    """Delete the password for the given service/account from the keychain."""

    try:
        GenericPassword(service, account).delete()
    except KeychainItemNotFoundError:
        pass


def set_password(service, account, password):
    """Save a password for the given service and account in the keychain."""

    GenericPassword(service, account).set_password(password)


def get_password(service, account):
    """Get the password for the given service/account that was previously stored in the keychain."""

    try:
        return GenericPassword(service, account).get_password()
    except KeychainItemNotFoundError:
        # Compatibility - Pythonista returns None if there's no password
        return None


def get_services():
    """Return a list of all services and accounts that are stored in the keychain (each item is a 2-tuple)."""

    try:
        return [
            (x.service, x.account)
            for x in GenericPassword.query_items()
        ]
    except KeychainItemNotFoundError:
        # Compatibility - Pythonista returns empty List if there're no passwords
        return []


def reset_keychain() -> Union[None]:
    """Delete all data from the keychain (including the master password) after showing a confirmation dialog.

    Raises:
        NotImplementedError: Always raised, not implemented and never will be."""

    raise NotImplementedError('Use Pythonista keychain.reset_keychain() if you really need it')
