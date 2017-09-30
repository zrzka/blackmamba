.. _install:

############
Installation
############

Install
-------

.. code-block:: python

    import requests as r; exec(r.get('http://bit.ly/get-blackmamba').text)

Copy the above line, paste into Pythonista interactive prompt and execute it.
Black Mamba will be installed under the ``site-packages-3`` folder.


Update
------

Black Mamba checks for updates automatically (once a day). If you'd like to
modify this behavior, read :ref:`configuration` section.

Updates are **not** installed automatically. Black Mamba just informs you
about available update. Copy & paste the installation line into Pythonista
interactive prompt again to update Black Mamba.


PIP
---

If you have `StaSh <https://github.com/ywangd/stash>`_ installed and you do use
``dev`` branch, you can use ``pip`` to install / update Black Mamba. Why ``dev``?
``pip`` in ``master`` does use XML-RPC, which is a legacy PyPI API.
`This pull request <https://github.com/ywangd/stash/pull/269>`_ replaces it with
JSON API and is merged into ``dev`` only.

So, you've got ``StaSh`` & ``dev``?

.. code-block:: bash

    pip install blackmamba -d ~/Documents/site-packages-3

How to update Black Mamba via ``pip``? Until `this PR <https://github.com/ywangd/stash/pull/272>`_
will be merged, you have to:

.. code-block:: bash

    pip remove blackmamba
    pip install blackmamba -d ~/Documents/site-packages-3


Startup
-------

Black Mamba requires you to put following lines to the ``~/Documents/site-packages-3/pythonista_startup.py``
file:

.. code-block:: python

    #!python3
    import blackmamba

    blackmamba.main()


This is bare minimum. Continue to :ref:`configuration` section to learn how to configure
Black Mamba behavior.
