# Change log

## master (unreleased)

* `pythonista_startup.py` sample - execute `main` only if `appex.is_running_extension()` is false
* Black Mamba supports Pythonista >= 3.2 & Python >= 3.6 only
    * Keyboard shortcuts added to Pythonista 3.2 removed
    * Removed `script/new_tab.py`, it was there just for `Cmd T`
    * Black Mamba fails to initialize if you do use with Pythonista < 3.2 || Python < 3.6
* `outline_quickly.py`
    * Added support for `async` functions
    * Added support for `TODO` and `FIXME`
        * Supported variants `TODO`, `TODO:`, `[TODO]`, case insensitive
        * re for TODO `'\A.*#\s*\[?(?i:TODO)\]?[ :]*(?P<text>.*?)\s*\Z'` as an example
        * Square brackets because of ligatures in [Pragmata Pro](https://www.fsd.it/shop/fonts/pragmatapro/)
        * Not perfect, matches if it's in the string, but it's good enough for now
* `forum-copy-code.py` script added
    * Allows you to copy code elements from the forum
* `blackmamba.framework.security`
    * Fixed InternetPassword query (check for not empty auth type)

## 1.5.0 (2018-01-11)

* Pass `-p no:cacheprovider` to fix operation not permitted for `.cache` directory (run unit tests script)
* Documentation cleanup and rewrite to Markdown, which is easily editable in Pythonista compared to reST
* `blackmamba.framework.security` introduced
* `blackmamba.uikit.keyboard`
    * Camel case enum constant deprecated, will be removed in 2.0.0
    * Use UPPER_CASED versions, camel case still exists as aliases
* `with bundle()` always unloads `pkg_resources.*` causing issues
    * Launch Pythonista, run Black Mamba Analyze - works vs
    * Launch Pythonista, run Pythonista unit tests, run Black Mamba Analyze - fails, because of `pkg_resources`

## 1.4.3 (2017-12-30)

* Compatibility check with 3.2 (320000)

## 1.4.2 (2017-12-23)

* Compatibility check with 3.1.1 (311017)

## 1.4.1 (2017-11-13)

* Compatibility check with 3.1.1 (311016)
* Bundle `refactoring` enhanced with `future`, `libfuturize`, `libpasteurize` modules
* `script/refactoring/futurize.py` introduced (see [Python Future](https://github.com/PythonCharmers/python-future))
    * Equivalent of `futurize -1 --all-imports -n -w --add-suffix 3 $editor.get_path()` (Stage 1 only)
    * When futurizer ends, editor text is replaced with content of the `.py3` and `.py3` is trashed
    * You can run futurizer script with `Cmd Option F`
* Improved updates check
    * Console is not cluttered with local / latest release info (installer prints this)
    * Update `check()` doesn't ask if update should (not) be installer (installer also asks)
    * If there's new update available, installer is executed, you will still be asked (just once, not twice)
* Script `new_file.py` modified
    * File opened
        * Asks for a file name (empty & `Enter` -> Cancel)
        * New file path is currently opened file dirname + entered file name
        * If file doesn't exist, new file is created and opened
        * If file exists, file is opened
    * No file opened
        * Same behavior as now
        * New tab created and _New File..._ button tap emulated
* Installer
    * Replaced `ModuleNotFoundError` (Python 3.6) with `ImportError` (Python 3.5)

## 1.4.0 (2017-11-01)

* Fixed keyboard shortcut selector name generator
* Bundle `refactoring` introduced (includes `rope`)
* Refactoring functions introduced
    * It's an EXPERIMENT. You should use version control system to avoid loosing data.
    * `Cmd Option O` - Organize imports
    * `Cmd Option E` - Expand star imports
    * `Cmd Option R` - Rename identifier
    * Can be used as scripts as well, see `script/refactoring` folder
    * Preview dialog can be closed with `Cmd .` / `Esc`, confirmed with `Enter`
* Scroll back to initial cursor location if analyzer didn't find an issue, ugly, but better than end of the file

## 1.3.3 (2017-10-27)

* Installer improved
    * Print installed version to the console
    * Show installed version in the dialog update/replace dialog
    * Dialog content differs for update/replace (version comparison)
* `script/selfupdate.py` added (it just runs installer via requests)
* Check for updates
    * Update dialog allows you to run `selfupdate.py`
    * If you hit cancel, installer command is copied to the clipboard
      and additional info about `selfupdate.py` / installer command
      is printed to the console

## 1.3.2 (2017-10-25)

* Fixed exception when there's empty tab opened (#30)
* Open quickly selects proper tab when the file is already opened
  and empty tab exists as well
* Compatibility check with 311015
    * `Cmd-Shift-]`, `Cmd-Shift-[` registered only in Pythonista < 311015
    * These shortcuts are natively supported
* flake8-3.5.0, pyflakes-1.6.0
    * Bare exception check
    * Ambigious identifier check  

## 1.3.1 (2017-10-19)

* Run scripts via `pythonista3://`, not just `pythonista://` (see #29)

## 1.3.0 (2017-10-19)

* Pythonista 3.1.1 (311014)
    * Compatibility check with 311014
    * Shortcuts `Cmd W`, `Ctrl [Shift] Tab` work
* Trashed `Cmd Q` shortcut (workaround for 311013)
* Open Quickly supports File System Provider bookmarks
    * You can search / open files added to Pythonista via `Open...` (External files)
    * These files are added as bookmarks (iOS terminology)
    * If cell subtitle starts with `Documents`, it's a file from `~/Documents`
    * If cell subtitle starts with `Bookmark`, it's a file from FSP

## 1.2.2 (2017-10-18)

* Bundled `lib/pep8` removed, unused
* Fixed `get_actions` (exception when user has no custom actions)
* Pythonista 3.1.1 (311013)
    * Compatibility check with 311013
    * Shortcuts `Cmd W`, `Ctrl Tab`, `Ctrl Shift Tab` no longer work (1)
    * Shortcuts `Cmd 1..9`, `Cmd Shift ]`, `Cmd Shift [`, `Cmd Shift W` still work

(1) Pythonista 311013 provides these shortcuts natively. Unfortunately,
they do not work. Also these shortcuts are provided elsewhere in the
responder chain, so, even if I register them via the Black Mamba, responder
chain catches them sooner then Black Mamba and they do not work.

All these shortcuts do work prior to 311013. If you have 311013 installed, you
can use `Cmd Q` to close tab (temporary) and `Cmd Shift ]` / `Cmd Shift [`
to show next / previous tab.

## 1.2.1 (2017-10-11)

* [Bundled packages](http://blackmamba.readthedocs.io/en/stable/bundled.html) links and licenses
* `ide.run_script` respects `delay` argument (did contain hardcoded value)
* Analyze script documentation mentions `flake8`
* Drag & Drop script
    * Children nodes are lazy-loaded (faster)
    * Dropped folder reloads ...
        * Target row if not expanded (to display triangle)
        * Children nodes (dropped folder appears if it didn't exist before drop)
* Show documentation
    * Do not show picker / docstring if symbol was found, but it has no docstring


## 1.2.0 (2017-10-10)

* `.uikit.overlay` introduced which allows Black Mamba to display information as overlays
    * Overlays are Pythonista app overlays (visible in editor, console, ...)
* `.ide.theme` introduced to get some theme functionality
* Show documentation script leverages new overlays
    * Overlay can be closed via `Ctrl W` shortcut
    * Overlay can be moved (title bar)
    * Overlay can be resized (drag bottom left/right corner)
    * Script is configurable, see [docs](http://blackmamba.readthedocs.io/en/stable/user/configuration.html#documentation)
    * See [screenshot](http://blackmamba.readthedocs.io/en/stable/gallery.html#inline-documentation) (reuse disabled)


## 1.1.0 (2017-10-05)

* [Dropped PyPI packaging](http://blackmamba.readthedocs.io/en/stable/user/install.html#pip)
    * Black Mamba provides own / updated modules to provide new functionality
    * This is not compatible with `pip` at all, thus this installation method is no longer supported
    * Latest Black Mamba release in PyPI is 1.0.2
* Find usages contains symbol name in the dialog title
* Jump to definition contains symbol name in the dialog title
* Show documentation contains symbol name in the dialog title
* `tab.open_file` has new `line` argument
    * Jump to definition, Find usages utilizes `tab.open_file` instead of `editor`'s one
* Analyze script does use bundled `flake8`, 'mccabe`, ...
    * See [documentation](http://blackmamba.readthedocs.io/en/stable/user/configuration.html#analyzer) to check how to configure it
    * First pass defaults are `['--select=E901,E999,F821,F822,F823']`
    * Second pass defaults are `['--max-complexity=10', '--max-line-length=127']`
* Open quickly, ... filter is case insensitive


## 1.0.2 (2017-10-01)

* Fixed Black Mamba for stable Pythonista version (Python 3.5)


## 1.0.1 (2017-10-01)

* Fixed unit tests annotations


## 1.0.0 (2017-10-01)

* Development status changed to `5 - Production/Stable`
* Fixed programming language classifier (Python 3.6)
* Detailed documentation available at [blackmamba.readthedocs.io](http://blackmamba.readthedocs.io)
    * Contains About, User Guide, Reference, Contribution, Development and FAQ
    * If you're just Black Mamba user, read User Guide
    * If you'd like to use Black Mamba functions, read Reference
* Dialogs
    * Keyboard shortcut to close dialogs (`Ctrl [`) replaced with `Cmd .` (Apple one)
    * Default width is 80% of window width (max 700)
    * Default height is 80% of window height
* Open, run, action, ... dialogs
    * Properly sorted items (by lowercased file names)
    * Filtering works on folders too
        * `bl __init` matches any file where full path does contain `bl` and `__init`
        * Folders up to `~/Documents` are not matched, only subfolders of `~/Documents`
* Drag & Drop
    * New way how a folder / file is provided
    * Works with [Kaleidoscope](https://www.kaleidoscopeapp.com/) for example
    * Still compatible with Working Copy
    * All opened files are listed in the dialog
* Open Quickly
    * If file is already opened, tab with file is selected
* Find usages
    * It actually did show definitions instead of usages, fixed
* Some other bugfixes I can't recall now

## 0.0.27 (2017-09-22)

* Drag provider trashed (`Cmd E`)
* Drag & Drop introduced (`Cmd E`)
    * Allows bidirectional drag & drop of files & folders & repos
    * List of ignored folders is configurable via `drag_and_drop.ignored_folders`,
      check [config.py](https://github.com/zrzka/blackmamba/blob/master/blackmamba/config.py)
      for default values
    * Can be used as wrench menu icon (`script/drag_and_drop.py`)

There's one limitation (will be fixed). Whenever you drop folder from Working
Copy, UI isn't updated and you have to close Drag & Drop window and open it again
to see this folder.


## 0.0.26 (2017-09-21)

* Jump to definition fixes
* Jedi - ignore definitions if there's no path & line number
* `blackmamba.project` trashed (replaced with Jedi, thanks to @JonB)
* Jump to definition shortcut synced with Xcode (`Control Command J`)
* Find usages added (`script/find_usages.py` & `Control Command U`)
* Show documentation (`script/show_documentation.py` & `Control Command ?`)
    * Displayed as `success` annotation on the current line
    * You can clear annotation with `Cmd Shift K` (already there)
* All these three featues does `jedi` now. Jedi is not thread safe and
  because I had not lot of time to investigate how and when is the Jedi
  used by Pythonista, I decided to disable these three features by
  default. To enable them, just set `general.jedi` to `True` when
  passing configuration to the `main`.
  
BTW this `.` notation is a shortcut for documentation and you have to pass
it as dictionary:
  
```python
config = {
    'general': {
        'jedi': True
    }
}

blackmamba.main(config)
```


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
