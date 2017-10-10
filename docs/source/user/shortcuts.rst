.. _shortcuts:

##################
Keyboard shortcuts
##################

General
=======

``Cmd 0`` toggles file navigator / library.


Dialogs
=======

You can close all dialogs with ``Esc`` key. Use ``Cmd .`` if you have a keyboard without
``Esc`` key.

Dialogs with tables support arrow keys to change selection and ``Enter`` key to select item.

Some of these dialogs support ``Shift Enter`` for an alternate action.
Example is the Open Quickly script where you can open file in a new tab (``Enter``)
or in the current tab (``Shift Enter``).


Tabs
====

``Cmd 1`` .. ``Cmd 9`` quickly switches between tabs.

``Ctrl Tab`` or ``Cmd Shift ]`` selects next tab and
``Ctrl Shift Tab`` or ``Cmd Shift [`` selects previous tab.

``Cmd W`` closes current tab and ``Cmd Shift W`` closes all tabs except
current one.

``Cmd T`` creates new empty tab and ``Cmd N`` shows Pythonista new file
dialog.


Editor
======

``Ctrl Up`` for page up, ``Ctrl Down`` for page down. Page
line count is configurable, see :ref:`configuration`.


Scripts
=======

:ref:`scripts` keyboard shortcuts binding:

================  ========
Shortcut          Function
================  ========
``Cmd E``         Drag & Drop
``Cmd /``         Toggle comments
``Cmd Shift O``   Open quickly
``Cmd Shift 0``   Search `Dash <https://kapeli.com/dash_ios>`_
``Cmd Shift R``   Run quickly
``Cmd Shift A``   Action quickly
``Ctrl Shift B``  Analyze
``Cmd Shift K``   Clear annotations
``Cmd U``         Run unit tests
``Cmd Shift L``   Outline quickly
``Ctrl L``        Jump to line
``Ctrl Cmd J``    Jump to definition
``Ctrl Cmd U``    Find usages
``Ctrl Cmd ?``    Show documentation
``Ctrl W``        Close active overlay [#f1]_
================  ========

.. [#f1] Show documentation script does use overlays.

Just hold ``Cmd`` key and iOS will show you all available shortcuts
if you can't remember them.


Custom shortcuts
================

See :ref:`blackmamba.uikit.keyboard` to learn how to register custom keyboard shortcuts.
