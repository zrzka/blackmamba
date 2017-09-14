==========
Change Log
==========

``master`` (unreleased)
-----------------------

*

``0.0.22`` (2017-09-14)
-----------------------

* Toggle comments improved
    * Honors both tabs and spaces
    * Indented ``#`` if line is indented
    * Shortest indent is used for all lines ``#`` if commenting multiple of them
    * Empty lines are ignored
* Fixed ``ide.run_action`` when ``script_name`` starts with ``/``


``0.0.21`` (2017-09-11)
-----------------------

* Config option to disable keyboard shortcuts registration


``0.0.20`` (2017-09-11)
-----------------------

* Code cleanup (circular deps, ...)
* Fixed analyzer where ``ignore_code=None`` means real ``None``
* Please, check sample ``pythonista_startup.py``, breaking changes, sry


``0.0.19`` (2017-09-05)
-----------------------

* Fixed unused import in action picker
* Compatibility check with 3.1.1 (311009)
* Introduced ``ide.scroll_to_line(line_number)``
* ``Ctrl L`` Jump to line... added
* ``Cmd E`` to show Drag Provider (iOS 11 only)


``0.0.18`` (2017-09-04)
-----------------------

* Installation command is copied to the clipboard when the alert about
  new version is shown. Just open console and paste it.
* ``system.Pythonista`` and ``system.iOS`` decorator to limit functions
  execution under the specific Pythonista & iOS versions.
* 0.0.17 skipped, because this version was used for testing & fixing pip
* Outline Quickly... (``Cmd Shift L``) introduced


``0.0.16`` (2017-08-29)
-----------------------

* Allow to start Black Mamba even in untested version of Pythonista, just
  warn the user
* Init messages are colored (orange=warn, red=error)
* All print messages replaced with ``log.info`` (``.error``, ``.warn``)
* ``bm.log.level`` allows to set logging level (default ``INFO``)
* Do not bother user with alert about new version (just use console)
  in case the Black Mamba is not installed via installer (git for example)
* Tested with latest Pythonista beta (3.1.1 - 311008)
 

``0.0.15`` (2017-08-28)
-----------------------

* Fix HUD message when there're no tests in the file
* Removed unreliable PyPI package installation option
* Removed package from PyPI
* Custom installer alla StaSh
* Removed ``settings`` module (moved to respective modules)
* Removed ``script_picker.py`` (merged to ``file_picker.py``)
* Updated ``pythonista_startup.py`` sample
* Pythonista version compatibility check

``0.0.14`` (2017-08-25)
-----------------------

* Since 0.0.14, the license was to changed to MIT
* Seems no one does use PyPI for installation, .pyui files are now included :)
* Comment line with ``# `` instead of just ``#`` (#12)
* ``Ctrl Tab`` (or ``Cmd Shift ]``) selects next tab
* ``Ctrl Shift Tab`` (or ``Cmd Shift [``) selects previous tab
* ``Cmd 1..9`` selects specific tab
* EXPERIMENTAL ``Cmd U`` to run unit tests (works, but sometimes, use at your
  own risk)


``0.0.13`` (2017-08-24)
-----------------------

* flake8 checks on Travis CI (thanks to cclauss)
* Fixed all style issues from flake8 report, down to zero now
* Analyzer removes trailing white spaces & trailing blank lines
  before analysis is started (can be turned off via ``bm.settings...``)
* Fixed toggle comments script (#5)
* Fixed file matching in Open Quickly... (#10)
* Fixed Esc key code (27 = X, not Esc, Esc = 41) (#11)


``0.0.12`` (2017-08-24)
-----------------------

* Analyze renamed to Analyze & Check Style
* Analyzer now runs both pyflakes & pep8 code style checks
* Analyzer behavior can be modified via ``bm.settings.ANALYZER_*``
* Analyzer always scrolls to the first issue
* Analyzer shows HUD only if there're no issues
* ``Cmd Shift K`` introduced to clear annotations


``0.0.11`` (2017-08-23)
-----------------------

* New tab shortcut changed to ``Cmd-T`` (reported by Ole)
* Open quickly shortcut synced with Xcode to ``Cmd-Shift-O`` (reported by Ole)
* ``Ctrl-Shift-B`` to clear annotations & analyze file (bundled pyflakes)


``0.0.10`` (2017-08-22)
-----------------------

* Allow to specify folders to ignore for Run/Open Quickly... via ``blackmamba.settings``
* ``Run Script Quickly...`` renamed to ``Run Quickly...``
* New ``blackmamba.ide`` functions - ``run_script``, ``script_exists``, ``run_action``,
  ``action_exists``
* ``key_commands.register_key_command`` prints shortcut in a nicer way along with package
  & function name
 
