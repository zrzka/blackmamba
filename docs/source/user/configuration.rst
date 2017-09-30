.. _configuration:

#############
Configuration
#############


Default configuration
=====================

Here's the default Black Mamba configuration.

.. code-block:: python

    {
        'general': {
            'jedi': False,
            'register_key_commands': True,
            'page_line_count': 40
        },
        'update': {
            'enabled': True,
            'interval': 3600
        },
        'file_picker': {
            'ignore_folders': {
                '': ['.git'],
                '.': ['.Trash', 'Examples',
                      'site-packages', 'site-packages-2', 'site-packages-3']
            }
        },
        'analyzer': {
            'hud_alert_delay': 1.0,
            'ignore_codes': None,
            'max_line_length': 127,
            'remove_whitespaces': True
        },
        'tester': {
            'hud_alert_delay': 1.0,
            'hide_console': True
        },
        'drag_and_drop': {
            'ignore_folders': {
                '': ['.git'],
                '.': ['.Trash', 'Examples',
                      'site-packages', 'site-packages-2', 'site-packages-3', 'stash_extensions']
            }
        }
    }

general
=======

jedi
----

`JEDI <http://jedi.readthedocs.io/en/latest/>`_ is used as a backend for Find usages,
Jump to definition and Show documentation :ref:`scripts`.

But because JEDI is also used by Pythonista, JEDI is not thread safe
and I don't know when and how it is used, it's disabled by default.

Set it to ``True`` to enable mentioned scripts.

register_key_commands
---------------------

Controls if default :ref:`shortcuts` are registered during Black Mamba startup or not.

page_line_count
---------------

Number of lines to scroll up / down for page up / down.


update
======

enabled
-------

Set to `False` if you'd like to disable updates.

interval
--------

Update check interval in seconds, updates are checked only during Black Mamba startup.


file_picker
===========

Used by Open quickly and Run quickly :ref:`scripts`.

ignore_folders
--------------

Key is parent directory name (not full path, just name). Two special values
are supported:

* ``''`` - any parent directory
* ``'.'`` - parent directory is ``~/Documents``

Example:

.. code-block:: python

    'ignore_folders': {
        '': ['.git'],
        '.': ['.Trash', 'Examples',
              'site-packages', 'site-packages-2', 'site-packages-3']
    }

It says that ``.git`` folder inside any folder is ignored. And ``.Trash``,
``Examples``, ... folders inside ``~/Documents`` folder are ignore as well.


Sample configuration
====================

.. note:: Passed configuration is **merged** with the default one. You can
   make it much more shorter if you're happy with default values.

Example of ``~/Documents/site-packages-3/pythonista_startup.py``:

.. code-block:: python

    import blackmamba
    import blackmamba.log as log

    # Default value is INFO. Use ERROR if you'd like to make Black
    # Mamba quiet. Only errors will be printed.
    log.set_level(log.INFO)

    # Check blackmamba.config._DEFAULTS for default values
    config = {
        'general': {
            'jedi': True
            # Uncomment to disable keyboard shortcuts
            # 'register_key_commands': False
        },
        'update': {
            'enabled': True,
            'interval': 3600
        },
        'file_picker': {
            'ignore_folders': {
                '': ['.git'],
                '.': ['.Trash', 'Examples', 'stash_extensions']
            }
        },
        'analyzer': {
            'hud_alert_delay': 1.0,
            'ignore_codes': ['E114', 'E116'],
            'max_line_length': 127,
            'remove_whitespaces': True
        },
        'tester': {
            'hud_alert_delay': 1.0,
            'hide_console': True
        },
        'drag_and_drop': {
            'ignore_folders': {
                '': ['.git'],
                '.': ['.Trash', 'Examples', 'stash_extensions']
            }
        }
    }


    def register_custom_shortcuts():
        import blackmamba.ide.action as action
        from blackmamba.uikit.keyboard import register_key_command, UIKeyModifier

        # Launch `StaSh` (= custom action title) via Ctrl-S
        action = action.get_action('StaSh')
        if action:
            def launch_stash():
                action.run()

            register_key_command(
                'S',
                UIKeyModifier.control,
                launch_stash,
                'Launch StaSh'
            )


    def main():
        # The only requirement is to call main(). You can omit `config=config`
        # if you'd like to use default config.
        blackmamba.main(config=config)
        register_custom_shortcuts()

        # If you'd like to hide console after Black Mamba starts, just uncomment
        # following lines
        # import console
        # console.hide_output()


    if __name__ == 'pythonista_startup':
        main()
