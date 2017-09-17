# Change log

## master (unreleased)

* `blackmamba.project` trashed (replaced with Jedi, thanks to )
* Jump to definition does use Jedi directly
* Jump to definition shortcut synced with Xcode (`Control Command J`)
* Find usages added (`script/find_usages.py` & `Control Command U`)


## 0.0.25 (2017-09-16)

* `blackmamba.script` introduced and it does contain following scripts
    * `action_quickly.py`, `analyze.py`, `clear_annotations.py`, `close_all_tabs_except_current_one.py`,
      `drag_provider.py`, `jump_to_definition.py`, `jump_to_line.py`,  `new_file.py`, `new_tab.py`,
      `open_quickly.py`, `outline_quickly.py`, `run_quickly.py`, `run_unit_tests.py`,  `search_dash.py`,
      `toggle_comments.py`
    * These scripts can be used in the wrench icon (action)
    * These scripts are binded to keyboard shortcuts, whenever you run it via wrench icon
      or via keyboard shortcut, esame script is executed
    * It's still required to call `blackmamba.main` from within
      `~/Documents/site-packages-3/pythonista_startup.py` file to properly configure it
      (even without external keyboard)
* Drag Provider uses Pythonista title bar instead of custom title to allow users to close the
  the dialog without external keyboard
* Unit tests (`tester.py`) moved from `blackmamba.experimental` to `blackmamba`
* `ide.run_script` and `ide.run_action` has new args named `delay`, which defaults to `None`
* Run Quickly & Action Quickly runs scripts with 1.0s delay and that's because
  both these actions are binded to scripts in the new script folder and if there's no
  delay, nothing happens if these scripts are Python 3 (basically it runs script from script,
  which doesn't ended yet)
* Fixed #20 (Pythonista appex error)
    * Allow to run `main`
    * Do not check compatibility, updates
    * Do not register keyboard shortcuts
* `blackmamba.system.Pythonista` decorator has new arg `appex`
    * Defaults to `None`
    * `appex=True` - run decorated function if it's running as application extension
    * `appex=False` - run decorated function if it's not running as application extension
    * `appex=None` - run in both case, just don't check
* `blackmamba.key_command.register_key_command` is decorated with `Pythonista(appex=False)`
   to avoid shortcut registration if it's running as application extension
* Page Up (`Ctrl Up`) and Page Down (`Ctrl Down`)
    * It jumps up / down by 40 lines by [default](https://github.com/zrzka/blackmamba/blob/master/blackmamba/config.py#L17)
    * You can modify this value via `general.page_line_count`
    * See [#395](https://github.com/omz/Pythonista-Issues/issues/395), it's recommended
      to hit Left / Right arrow key after page up / down to workaround iOS / Pythonista bug


## 0.0.24 (2017-09-15)

* `blackmamba.keyboard` module added
* Pickers (open, script, ... quickly)
    * Do not focus search field if HW keyboard is not connected
    * Show title bar instead of custom title to allow users to close
      dialogs with X button
* `ide.scroll_to_line` optimized
* Toggle comments various fixes
    * Line is properly commented when there's inline comment
    * Uncommented line -> whitespaces only -> '\n'
    * More test coverage to avoid future bugs


## 0.0.23 (2017-09-14)

* Jump to definition (`Cmd Shift D`)


## 0.0.22 (2017-09-14)

* Toggle comments improved
    * Honors both tabs and spaces
    * Indented `#` if line is indented
    * Shortest indent is used for all lines `#` if commenting multiple of them
    * Empty lines are ignored
* Fixed `ide.run_action` when `script_name` starts with `/`


## 0.0.21 (2017-09-11)

* Config option to disable keyboard shortcuts registration


## 0.0.20 (2017-09-11)

* Code cleanup (circular deps, ...)
* Fixed analyzer where `ignore_code=None` means real `None`
* Please, check sample `pythonista_startup.py`, breaking changes, sry


## 0.0.19 (2017-09-05)

* Fixed unused import in action picker
* Compatibility check with 3.1.1 (311009)
* Introduced `ide.scroll_to_line(line_number)`
* `Ctrl L` Jump to line... added
* `Cmd E` to show Drag Provider (iOS 11 only)


## 0.0.18 (2017-09-04)

* Installation command is copied to the clipboard when the alert about
  new version is shown. Just open console and paste it.
* `system.Pythonista` and `system.iOS` decorator to limit functions
  execution under the specific Pythonista & iOS versions.
* 0.0.17 skipped, because this version was used for testing & fixing pip
* Outline Quickly... (`Cmd Shift L`) introduced


## 0.0.16 (2017-08-29)

* Allow to start Black Mamba even in untested version of Pythonista, just
  warn the user
* Init messages are colored (orange=warn, red=error)
* All print messages replaced with `log.info` (`.error`, `.warn`)
* `bm.log.level` allows to set logging level (default `INFO`)
* Do not bother user with alert about new version (just use console)
  in case the Black Mamba is not installed via installer (git for example)
* Tested with latest Pythonista beta (3.1.1 - 311008)
 

## 0.0.15 (2017-08-28)

* Fix HUD message when there're no tests in the file
* Removed unreliable PyPI package installation option
* Removed package from PyPI
* Custom installer alla StaSh
* Removed `settings` module (moved to respective modules)
* Removed `script_picker.py` (merged to `file_picker.py`)
* Updated `pythonista_startup.py` sample
* Pythonista version compatibility check


## 0.0.14 (2017-08-25)

* Since 0.0.14, the license was to changed to MIT
* Seems no one does use PyPI for installation, .pyui files are now included :)
* Comment line with `# ` instead of just `#` (#12)
* `Ctrl Tab` (or `Cmd Shift ]`) selects next tab
* `Ctrl Shift Tab` (or `Cmd Shift [`) selects previous tab
* `Cmd 1..9` selects specific tab
* EXPERIMENTAL `Cmd U` to run unit tests (works, but sometimes, use at your
  own risk)


## 0.0.13 (2017-08-24)

* flake8 checks on Travis CI (thanks to cclauss)
* Fixed all style issues from flake8 report, down to zero now
* Analyzer removes trailing white spaces & trailing blank lines
  before analysis is started (can be turned off via `bm.settings...`)
* Fixed toggle comments script (#5)
* Fixed file matching in Open Quickly... (#10)
* Fixed Esc key code (27 = X, not Esc, Esc = 41) (#11)


## 0.0.12 (2017-08-24)

* Analyze renamed to Analyze & Check Style
* Analyzer now runs both pyflakes & pep8 code style checks
* Analyzer behavior can be modified via `bm.settings.ANALYZER_*`
* Analyzer always scrolls to the first issue
* Analyzer shows HUD only if there're no issues
* `Cmd Shift K` introduced to clear annotations


## 0.0.11 (2017-08-23)

* New tab shortcut changed to `Cmd-T` (reported by Ole)
* Open quickly shortcut synced with Xcode to `Cmd-Shift-O` (reported by Ole)
* `Ctrl-Shift-B` to clear annotations & analyze file (bundled pyflakes)


## 0.0.10 (2017-08-22)

* Allow to specify folders to ignore for Run/Open Quickly... via `blackmamba.settings`
* `Run Script Quickly...` renamed to `Run Quickly...`
* New `blackmamba.ide` functions - `run_script`, `script_exists`, `run_action`,
  `action_exists`
* `key_commands.register_key_command` prints shortcut in a nicer way along with package
  & function name
