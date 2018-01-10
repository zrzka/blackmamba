# Scripts

Following scripts are usable as Pythonista action items (wrench menu icon). In other
words, you can use them even without external keyboard.

Scripts still requires you to call `blackmamba.main`, see [API Reference](../api/blackmamba.md).

## action_quickly.py

Shows dialog with user defined action items (wrench icon). You can filter them
by title, use arrow keys to change selection and run any of them with `Enter` key.

Only **user defined action items** are listed.

## analyze.py

Source code analysis with `flake8`. Results are displayed as
Pythonista annotations. If there's no error / warning, HUD informs you about that.

This script is configurable, see [Configuration](configuration.md#analyzer).

## clear_annotations.py

Clears all Pythonista annotations.

## close_all_tabs_except_current_one.py

Closes all tabs except current one.

## drag_and_drop.py
 
**iOS >= 11.0 required**.

Shows dialog with opened files and folders tree. You can drag a file / folder to
any other iOS application. Works well with [Working Copy](http://workingcopyapp.com/)
and [Kaleidoscope](https://www.kaleidoscopeapp.com/) for example.

You can drag a file / folder from any other iOS application as well. But there's one
limitation, you can drop them at the folder only.

This script is configurable, see [Configuration](configuration.md#drag-and-drop).

## find_usages.py

Finds usages of a symbol. If there're no usage, HUD informs you.
Otherwise dialog appears where you can select location and scroll to it.

JEDI must be enabled, see [Configuration](configuration.md#general).

## jump_to_definition.py

Jumps to symbol definition. If definition can't be found, HUD informs you.
Otherwise it jumps to definition location or shows dialog where you can choose
location if more than one definition was found.

JEDI must be enabled, see [Configuration](configuration.md#general).

## jump_to_line.py

Shows dialog where you can enter line number to scroll to.

## new_file.py

If there's no opened file in the Pythonista, new tab is created and *New File...*
button tap is emulated.

Otherwise dialog appears where you can enter new file name. File will be created
in the current folder. If it already exists, file will be opened instead of creating
new one.

## new_tab.py

Creates new empty tab.

## open_quickly.py

Shows dialog with all your files. You can filter these files by directories,
file name, etc. Use arrow keys to change selection and then hit `Enter` to open
selected file.

If file is already opened, Black Mamba changes selected tab only.

This script is configurable, see [Configuration](configuration.md#file-picker).

## outline_quickly.py

Shows source code outline. You can filter functions, ... by name. Use arrows key to
change selection and then hit `Enter` to scroll to the symbol.

## run_quickly.py

Shows dialog with all your Python files. You can filter these files by directories,
file name, etc. Use arrows keys to change selection and then hit `Enter` to
run selected file.

This script is configurable, see [Configuration](configuration.md#file-picker).

## run_unit_tests.py

Runs unit tests and show results as Pythonista annotations.

This script is configurable, see [Configuration](configuration.md#tester).

## search_dash.py

Opens [Dash](https://kapeli.com/dash_ios) application with selected text or a symbol around cursor position.

## show_documentation.py

Shows documentation for the symbol around cursor. If definition can't be found,
HUD informs you. If there're more than one definitions, dialog appears where
you can select which one to show.

Documentation is displayed as an overlay, which can be closed by the
`Ctrl W` shortcut or by tapping on the `X` button.

This script is configurable, see [Configuration](configuration.md#documentation).

JEDI must be enabled, see [Configuration](configuration.md#general).

## toggle_comments.py

Toggles current line / selected lines comments.

## Refactoring

All refactoring scripts are limited to single file only which must be opened.

It's an experiment. You should use version control system to avoid loosing data.

### expand_star_imports.py

Expand star imports.

### futurize.py

Runs stage 1 of the [futurizer](https://github.com/PythonCharmers/python-future).

### organize_imports.py

Organize imports.

### rename.py

Rename identifier.
