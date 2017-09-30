.. _scripts:

#######
Scripts
#######

Following scripts are usable as Pythonista action items (wrench menu icon). In other
words, you can use them even without external keyboard.


Action quickly
==============

Script name ``action_quickly.py``.

Shows dialog with user defined action items (wrench icon). You can filter them
by title, use arrow keys to change selection and run any of them with ``Enter`` key.

Only **user defined action items** are listed.


Analyze
=======

Script name ``analyze.py``.

Source code analysis with ``pep8`` and ``pyflakes``. Results are displayed as
Pythonista annotations. If there's no error / warning, HUD informs you about that.

This script is configurable, see :ref:`configuration`.


Clear annotations
=================

Script name ``clear_annotations.py``.

Clears all Pythonista annotations.


Close all tabs except current one
=================================

Script name ``close_all_tabs_except_current_one.py``.

Closes all tabs except current one.


Drag & Drop
===========

Script name ``drag_and_drop.py``. **iOS >= 11.0 required**.

Shows dialog with opened files and folders tree. You can drag a file / folder to
any other iOS application. Works well with `Working Copy <http://workingcopyapp.com/>`_
and `Kaleidoscope <https://www.kaleidoscopeapp.com/>`_ for example.

You can drag a file / folder from any other iOS application as well. But there's one
limitation, you can drop them at the folder only.

.. note:: If you drop a folder, folder tree is not refreshed. You have to close
   dialog and open it again to see a new folder. Will be fixed.

This script is configurable, see :ref:`configuration`.


Find usages
===========

Script name ``find_usages.py``.

Finds usages of a symbol. If there're no usage, HUD informs you.
Otherwise dialog appears where you can select location and scroll to it.

JEDI must be enabled, see :ref:`configuration`.


Jump to definition
==================

Script name ``jump_to_definition.py``.

Jumps to symbol definition. If definition can't be found, HUD informs you.
Otherwise it jumps to definition location or shows dialog where you can choose
location if more than one definition was found.

JEDI must be enabled, see :ref:`configuration`.


Jump to line
============

Script name ``jump_to_line.py``.

Shows dialog where you can enter line number to scroll to.


New file
========

Script name ``new_file.py``.

Shows Pythonista new file dialog.


New tab
=======

Script name ``new_tab.py``.

Creates new empty tab.


Open quickly
============

Script name ``open_quickly.py``.

Shows dialog with all your files. You can filter these files by directories,
file name, etc. Use arrow keys to change selection and then hit ``Enter`` to open
selected file.

If file is already opened, Black Mamba changes selected tab only.

This script is configurable, see :ref:`configuration`.


Outline quickly
===============

Script name ``outline_quickly.py``.

Shows source code outline. You can filter functions, ... by name. Use arrows key to
change selection and then hit ``Enter`` to scroll to the symbol.


Run quickly
===========

Script name ``run_quickly.py``.

Shows dialog with all your Python files. You can filter these files by directories,
file name, etc. Use arrows keys to change selection and then hit ``Enter`` to
run selected file.

This script is configurable, see :ref:`configuration`.


Run unit tests
==============

Script name ``run_unit_tests.py``.

Runs unit tests and show results as Pythonista annotations.

This script is configurable, see :ref:`configuration`.


Search Dash
===========

Script name ``search_dash.py``.

Opens `Dash <https://kapeli.com/dash_ios>`_ application with selected text or a symbol around cursor position.


Show documentation
==================

Script name ``show_documentation.py``.

Shows documentation for the symbol around cursor. If definition can't be found,
HUD informs you. If there're more than one definitions, dialog appears where
you can select which one to show.

Documentation is displayed as Pythonista annotation.

JEDI must be enabled, see :ref:`configuration`.


Toggle comments
===============

Script name ``toggle_comments.py``.

Toggles current line / selected lines comments.
