===========
Black Mamba
===========

.. image:: https://travis-ci.org/zrzka/blackmamba.svg?branch=master
    :align: right
    :alt: Travis CI Build Status

`Pythonista <http://omz-software.com/pythonista/>`_ on steroids.

    Pythonista is a complete development environment for writing Python™
    scripts on your iPad or iPhone.

Pythonista is a great tool. But it lacks some features like keyboard shortcuts
for specific actions. I'm slow without them. So I decided to write set of
scripts to *fix* all these issues. To speed up my iteration cycle. To make
it as fast as possible. And which snake is the speediest one on the planet?
`Black Mamba <https://en.wikipedia.org/wiki/Black_mamba>`_. And you know
why it's called Black Mamba now :)

.. contents:: Table of Contents

.. section-numbering::


Status
======

It's still an experiment and you can expect breaking changes. I'm trying
to avoid them, but I can't promise stable interface for now.

You're welcome to report `new issue <https://github.com/zrzka/blackmamba/issues/new>`_
if you find a bug or would like to have something added. Or `pull request
<https://github.com/zrzka/blackmamba/pulls>`_ which is even better.


Package Installation
====================

.. code-block:: python

    import requests as r; exec(r.get('http://bit.ly/get-blackmamba').text)

Copy the above line, paste into Pythonista interactive prompt and execute it.
Black Mamba will be installed under the ``site-packages-3`` folder.


Updates
-------

Black Mamba checks for updates automatically (once a day). This can be modified
via ``check_for_updates`` and ``check_interval`` variables in the ``updates``
module. Anyway, if you see a message about new version available, just repeat
package installation steps to install new version until real update will be
implemented.


pythonista_startup.py
=====================

Copy & paste ...

.. code-block:: python

    #!python3
    import blackmamba as bm
    bm.main()

... into ``~/Documents/site-packages-3/pythonista_startup.py`` and you're
ready to use following shortcuts:

==================  ========================================
Shortcut            Function
==================  ========================================
``Cmd /``           Comment / uncomment selected line(s)
``Cmd W``           Close current editor tab
``Cmd Shift W``     Close all editor tabs except current one
``Cmd N``           New tab + new file
``Cmd T``           Just new tab
``Cmd 0``           Show / hide navigator (Library)
``Cmd Shift 0``     Query selected text in Dash
``Cmd Shift O``     Open Quickly...
``Cmd Shift R``     Run Quickly...
``Cmd Shift A``     Action Quickly...
``Cmd Shift L``     Outline Quickly...
``Ctrl Shift B``    Analyze & Check Style
``Cmd Shift K``     Clear annotations
``Cmd U``           Run Unit Tests... (experimental)
``Ctrl Tab``        Show Next Tab (or ``Cmd Shift ]``)
``Ctrl Shift Tab``  Show Previous Tab (or ``Cmd Shift [``)
``Cmd 1..9``        Show nth tab
``Ctrl L``          Jump to line
``Cmd E``           Drag Provider
``Cmd Shift D``     Jump to definition...
==================  ========================================

**WARNING**: *Run Quickly...* and *Action Quickly...* works only and only
if there's no running script. If there's running script, you'll see
your script in the editor (new tab), but the script wasn't executed.


Do you want know more about configuration options? Check fully commented sample
`pythonista_startup.py <https://github.com/zrzka/blackmamba/blob/master/pythonista_startup.py>`_
file.

