==========
Change Log
==========

``master`` (unreleased)
-----------------------

* flake8 checks on Travis CI (thanks to cclauss)
* Fixed all style issues from flake8 report, down to zero now


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
 
