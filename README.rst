===========
Black Mamba
===========

`Pythonista <http://omz-software.com/pythonista/>`_ on steroids.

    Pythonista is a complete development environment for writing Python™
    scripts on your iPad or iPhone.

Pythonista is a great tool. But it lacks some features like keyboard shortcuts
for specific actions. I'm slow without them. So I decided to write set of
scripts to *fix* all these issues. To speed up my iteration cycle. To make
it as fast as possible. And which snake is the speediest one on the planet?
`Black Mamba <https://en.wikipedia.org/wiki/Black_mamba>`_. And you know
why it's called Black Mamba now :)

.. contents::

.. section-numbering::


Status
======

It's still an experiment and you can expect breaking changes. I'm trying
to avoid them, but I can't promise stable interface for now.

You're welcome to report `new issue <https://github.com/zrzka/blackmamba/issues/new>`_
if you find a bug or would like to have something added.


Installation
============

Install `StaSh - Shell for Pythonista <https://github.com/ywangd/stash>`_. All following
commands are for StaSh.


PyPI
----

    This is preferred way of installation.

**Initial installation:**

.. code-block:: bash

    [~/Documents]$ pip install blackmamba -d ~/Documents/site-packages-3

**Updates:**

.. code-block:: bash

    [~/Documents]$ pip update blackmamba


Git
---

You can use git way if you'd like to install Black Mamba from the master branch.
But it has several drawbacks:

* It's not officially released, can contain bugs, etc.
* You can't do this if you already have ``site-packages-3`` folder backed by
  the git (conflict with ``.git`` folder)

**Initial installation:**

.. code-block:: bash

    [~/Documents]$ cd site-packages-3
    [site-packages-3]$ git clone https://github.com/zrzka/blackmamba.git .

**NOTE**: Do not miss the space dot at the end of ``git clone`` command.

**Updates:**

.. code-block:: bash

    [~/Documents]$ cd site-packages-3
    [site-packages-3]$ git pull


Usage
=====

Following examples should be placed in the ``~/Documents/site-packages-3/pythonista_startup.py``
file. Create this file if it doesn't exist.


Ignore folders (Open/Run Quickly...)
------------------------------------

*Open/Run Quickly...* dialog ignores following folders by default:

* ``.git`` - in any folder
* ``.Trash``, ``Examples``, ``site-packages``, ``site-packages-2``, ``site-packages-3`` in ``~/Documents`` folder

You can modify it via:

* ``blackmamba.settings.OPEN_QUICKLY_IGNORE_FOLDERS`` - for *Open Quickly...* dialog
* ``blackmamba.settings.RUN_QUICKLY_IGNORE_FOLDERS`` - for *Run Quickly...* dialog

Example:

.. code-block:: python

    #!python3

    import blackmamba as bm

    bm.settings.OPEN_QUICKLY_IGNORE_FOLDERS = {
        # Ignores .git folder in any folder under ~/Documents
        '': ['.git'],
        
        # Ignores specific folders under . (= ~/Documents)
        # ~/Documents/Pythonista is ignored
        # ~/Documents/something/Pythonista is not ignored
        '.': ['Pythonista', '.Trash', 'Examples',
              'site-packages-2', 'site-packages', 'stash_extensions'],
              'site-packages-3': ['blackmamba'],
              
        # Ignores bm-pip-backup in ~/Documents/Development folder
        # Does not ignore bm-pip-backup folder in any other folder
        'Development': ['bm-pip-backup']
    }

    bm.settings.RUN_QUICKLY_IGNORE_FOLDERS = {
        '': ['.git'],
        '.': ['Pythonista', '.Trash', 'Examples',
              'site-packages-2', 'site-packages', 'stash_extensions'],
        'site-packages-3': ['blackmamba'],
        'Development': ['bm-pip-backup']
    }

    bm.register_default_key_commands()


Register default key commands
-----------------------------

.. code-block:: python

    #!python3

    import blackmamba as bm
    bm.register_default_key_commands()

This registers following keyboard shortcuts you can use with
external keyboard. It's optional, you're not forced to register
them.

===============  ========================================
Shortcut         Function
===============  ========================================
``Cmd /``        Comment / uncomment selected line(s)
``Cmd W``        Close current editor tab
``Cmd Shift W``  Close all editor tabs except current one
``Cmd N``        New tab + new file
``Cmd Shift N``  Just new tab
``Cmd 0``        Show / hide navigator (Library)
``Cmd Shift 0``  Query selected text in Dash
``Cmd O``        Open Quickly...
``Cmd Shift R``  Run Quickly...
``Cmd Shift A``  Action Quickly...
===============  ========================================

**WARNING**: *Run Quickly...* and *Action Quickly...* works only and only
if there's no running script. If there's running script, you'll see
your script in the editor (new tab), but the script wasn't executed.


Register custom key commands
----------------------------

How to print `Hallo` with `Cmd Shift H`.

.. code-block:: python

    #!python3

    from blackmamba.key_commands import register_key_command
    from blackmamba.uikit import *  # UIKeyModifier*

    def my_fn():
        print('Hallo')
    
    register_key_command('H', UIKeyModifierCommand | UIKeyModifierShift,
                         my_fn, 'Print Hallo')


Sample pythonista_startup.py
----------------------------

.. code-block:: python

    #!python3
    
    import blackmamba as bm
    
    #
    # '': any parent folder
    # '.': ~/Documents parent folder
    # 'Development': ~/Documents/Development parent folder
    #
    bm.settings.OPEN_QUICKLY_IGNORE_FOLDERS = {
        '': ['.git'],
        '.': ['Pythonista', '.Trash', 'Examples',
              'site-packages-2', 'site-packages', 'stash_extensions'],
        'site-packages-3': ['blackmamba'],
        'Development': ['bm-pip-backup']
    }
    
    bm.settings.RUN_QUICKLY_IGNORE_FOLDERS = {
        '': ['.git'],
        '.': ['Pythonista', '.Trash', 'Examples',
              'site-packages-2', 'site-packages', 'stash_extensions'],
        'site-packages-3': ['blackmamba'],
        'Development': ['bm-pip-backup']
    }
    
    #
    # Default Black Mamba external keyboard shortcuts registration
    #
    bm.register_default_key_commands()
    
    #
    # Custom shortcuts
    #
    
    def launch_stash():
        # Wrench item Custom Title (case sensitive)
        bm.ide.run_action('StaSh')
        
        # Or via script, relative path to ~/Documents
        # bm.ide.run_script('launch_stash.py')
        
    
    bm.key_commands.register_key_command(
        'S',
        bm.uikit.UIKeyModifierCommand | bm.uikit.UIKeyModifierShift,
        launch_stash,
        'Launch StaSh')

